# -*- coding: utf-8 -*-
"""
===============================================================================
module __InvasionPercolationForImbibition__: Invasion Percolation Algorithm for Imbibition
===============================================================================
"""
import scipy as sp
import numpy as np
import scipy.sparse as sprs
from time import clock
import heapq
import itertools
from OpenPNM.Algorithms import InvasionPercolation
from OpenPNM.Base import logging
logger = logging.getLogger(__name__)

class InvasionPercolationForImbibition(InvasionPercolation):
    r"""

    Invasion Percolation (Imbibition) with cluster growth timing - Class to run IP algorithm on constructed networks

    Parameters
    ----------
    network : Descendent of OpenPNM.Network.GenericNetwork
        A valid network for this algorithm
    name : string
        The name this algorithm will go by

    """
    def __init__(self,**kwords):
        r"""
        """
        super(InvasionPercolationForImbibition,self).__init__(**kwords)
        logger.info("Create IP Imbibition Algorithm Object")

    def run(self,invading_phase,
               defending_phase,
               inlets=[0],
               outlets=[-1],
               end_condition='breakthrough',
               pore_volume_name='volume',
               pore_diameter_name='diameter',
               throat_volume_name='volume',
               timing='ON',
               report=20,
               inlet_flow=1,
               Psecond=False,
               **params):
        r"""

        Invasion Percolation (Imbibition) with cluster growth timing - Class to run IP algorithm on constructed networks

        Parameters
        ----------
        invading_phase : OpenPNM Phase Object
            phase which will displace defending phase
        defending_phase : OpenPNM Phase Object
            phase which will be displaced by invading phase
        inlets : list of integers (default: [0])
            list of inlet nodes
        outlets : list of integers (default: [-1])
            list of outlet nodes
        end_condition : string('breakthrough')
            choice between 'breakthrough' and 'total'
        pore_volume_name : string('volume')
            name given to pore volume property
        pore_diameter_name : string('diameter')
            name given to pore diameter property
        throat_volume_name : string('volume')
            name given to throat volume property
        timing : string ('ON')
            turns volume and flowrate calculations 'ON' or 'OFF'
        report : int (20)
            percentage multiple at which a progress report is printed
        inlet_flow : float (1)
            m3/s for each cluster (affects timestamp of pore filling)
        Psecond : boul (False)
            is this a secondary imbibition (after drainage)?


        Input Phases
        ------------
        The algorithm expects an invading phase with the following pore properties:
            contact_angle, surface_tension
        and some defending phase

        Output
        ------
        The invading phase automatically gains pore data ::

            occupancy       : 0 for univaded, 1 for invaded
            IP_inv_final    : 0 for uninvaded, merged cluster number for invaded
            IP_inv_original : 0 for uninvaded, original cluster number for invaded
            IP_inv_seq      : 0 for uninvaded, simulation step for invaded
            IP_inv_time     : 0 for uninvaded, simulation time for invaded

        and throat data ::

            occupancy       : 0 for univaded, 1 for invaded
            IP_inv          : 0 for uninvaded, merged cluster number for invaded
            IP_inv_seq      : 0 for uninvaded, simulation step for invaded
            IP_inv_time     : 0 for uninvaded, simulation time for invaded

        Examples
        --------
        >>> import OpenPNM
        >>> pn = OpenPNM.Network.TestNet()
        >>> geo = OpenPNM.Geometry.TestGeometry(network=pn,pores=pn.pores(),throats=pn.throats())
        >>> phase1 = OpenPNM.Phases.TestPhase(network=pn)
        >>> phase1['pore.contact_angle'] = 20
        >>> phase2 = OpenPNM.Phases.TestPhase(network=pn)
        >>> phys1 = OpenPNM.Physics.TestPhysics(network=pn, phase=phase1,pores=pn.pores(),throats=pn.throats())
        >>> phys2 = OpenPNM.Physics.TestPhysics(network=pn, phase=phase2,pores=pn.pores(),throats=pn.throats())
        >>> from OpenPNM.Algorithms.__InvasionPercolationForImbibition__ import InvasionPercolationForImbibition
        >>> IP = InvasionPercolationForImbibition(network=pn)
        >>> IP.run(invading_phase=phase1, defending_phase=phase2, inlets=pn.pores('top'), outlets=pn.pores('bottom'))
             IP algorithm at 0 % completion at 0 seconds
             IP algorithm at 20 % completion at 0 seconds
             IP algorithm at 40 % completion at 0 seconds
             IP algorithm at 100% completion at  0  seconds
        >>> IP.return_results()
        >>> print(len(phase1.pores('occupancy')))
        29

        Suggested Improvements ::

            a) Allow updating of cluster flow-rates (this will require a delta-t calculation at each step, instead of a total t calculation).
            b) Allow for a non-linear relationship between pressure and throat-cap volume.

        """

        # if Psecond > 0 then we are doing a secondary imbibition,
        #   so end_condition, inlets, are treated differently
        self._Psecond = Psecond
        if Psecond:
            end_condition='secondary'
            inlets = [self._net.pores()[self._phase['pore.occupancy']>0]]
        self._timing = timing=='ON'
        self._pore_diameter_name = pore_diameter_name
        self._throat_volume_name = throat_volume_name

        super(InvasionPercolationForImbibition,self).run(invading_phase=invading_phase,
                                                       defending_phase=defending_phase,
                                                       inlets=inlets,
                                                       outlets=outlets,
                                                       end_condition=end_condition,
                                                       pore_volume_name=pore_volume_name,
                                                       timing=timing,
                                                       report=report,
                                                       inlet_flow=inlet_flow)

    def _setup_for_IP(self,**params):
        r"""
        Determines cluster labelling and condition for completion

        This code is taken from _setup_for_IP from parent InvasionPercolation, but is modified for imbibition

        """
        self._clock_start = clock()
        logger.debug( '+='*25)
        logger.debug( 'INITIAL SETUP (STEP 1)')
        # if empty, add Pc_entry to pore_properties
        # set the capillary pressure for pores, instead of throats
        #   don't need to interpolate for throats
        # this is a Washburn setting, could use others
        sigma = self._phase['pore.surface_tension'][0]
        theta = self._phase['pore.contact_angle'][0]
        if theta > 90:
            print('WARNING!!!: The invading phase has a contact angle greater than 90deg, so it must be drainage. Use Invasion_Percolation for drainage.' )
        pdia = self._net['pore.'+self._pore_diameter_name] 
        if self._Psecond:
            pdia = pdia[self._phase['pore.occupancy']<=0]
        # entry pressure for the pore
        # should be -4.. but use +4 to make heapq work correclty (we want highest Pcap)
        Pc_entry = -4*sigma*sp.cos(sp.radians(theta))/pdia     # -4*sigma*sp.cos(sp.radians(theta))/pdia     PCAP!!
        # add to the IPforImb object
        if ~self._Psecond:
            self._phase['pore.Pc_entryImb']=Pc_entry

        if self._timing:
            # calculate Volume_coef for each pore, not throat, for imbib
            # this is the volume of a half-sphere in the pore (so will work for irregular pores)
            self._Pvol_coef = pdia**3*np.pi/12/(Pc_entry)      # Pc_entry is stored -ve, so must be converted for vol_coeff    PCAP!!
        # Creating an array for invaded Pores(Np long, 0 for uninvaded, cluster number for inaveded)
        if self._Psecond:
            Np = sum(self._phase['pore.occupancy']<=0)
            Nt = sum(self._phase['throat.occupancy']<=0)
        else:
            Np = self._net.num_pores()
            Nt = self._net.num_throats()
        self._Pinv = np.zeros((Np,1),dtype=np.int32)
        self._Pinv_original = np.zeros((Np,1),dtype=np.int32)
        # Creating an array for invaded throats(Nt long, 0 for uninvaded, cluster number for inaveded)
        self._Tinv = np.zeros((Nt,1),dtype=np.int32)
        self._Tinv_original = np.zeros((Nt,1),dtype=np.int32)
        # Creating arrays for tracking invaded Pores(Np long, 0 for uninvaded, sequence for inaveded)
        self._psequence = np.zeros((Np,1),dtype=np.int32)
        if self._timing:
            # Creating arrays for tracking invaded Pores(Np long, -1 for uninvaded, simulation time for inaveded)
            self._Ptime = np.zeros((Np,1),dtype=np.float64)-1
        # Creating arrays for tracking invaded throats(Nt long, 0 for uninvaded, sequence for inaveded)
        self._tsequence = np.zeros((Nt,1),dtype=np.int32)
        if self._timing:
            # Creating arrays for tracking invaded Pores(Np long, -1 for uninvaded, simulation time for inaveded)
            self._Ttime = np.zeros((Nt,1),dtype=np.float64)-1
        # Creating an array for tracking the last invaded pore in each cluster.
        # its length is equal to the maximum number of possible clusters.
        #self.plists = np.zeros((len(self._inlets),1),dtype=np.int32)
        # Iterator variables for sequences and cluster numbers
        clusterNumber = 1
        # Determine how many clusters there are
        self._clusterCount = 0
        # get boundary pores so they don't get included in cluster count
        # bpores = self._net.pores(labels=['boundary','bottom'],mode='intersection')
        for i in self._inlets:
            #   ignore boundary pores
#            if ~sp.in1d(i,bpores): # don't need this anymore if all inlet pores are in the boundary
            self._clusterCount += 1
        # Storage for cluster information
        self._cluster_data = {}
        if self._timing:
            self._cluster_data['flow_rate'] = np.ones((self._clusterCount),dtype=np.float64)*self._inlet_flow
            self._cluster_data['haines_pressure'] = np.zeros((self._clusterCount),dtype=np.float64)
            self._cluster_data['haines_time'] = np.zeros((self._clusterCount),dtype=np.float64)
            self._cluster_data['vol_coef'] = np.zeros((self._clusterCount),dtype=np.float64)
            self._cluster_data['cap_volume'] = np.zeros((self._clusterCount),dtype=np.float64)
            self._cluster_data['throat_volume'] = np.zeros((self._clusterCount),dtype=np.float64)
        self._cluster_data['haines_pore'] = np.zeros((self._clusterCount),dtype=np.int32)
        self._cluster_data['active'] = np.ones((self._clusterCount),dtype=np.int8)
        self._cluster_data['transform'] = np.zeros((self._clusterCount),dtype=np.int16)
        for i in range(self._clusterCount):
            self._cluster_data['transform'][i] = i+1
        # Creating an empty list to store the list of potential pores for invasion in each cluster.
        # its length is equal to the maximum number of possible clusters.
        self._plists = []
        # Creating a list for each cluster to store both potential pore and corresponding pore value
        self._ppoints = []
        # Initializing invasion percolation for each possible cluster
        for i in self._inlets:
            if self._timing:
#                # Calculate total volume in all inlet pores
                self._cluster_data['throat_volume'][clusterNumber-1] = np.sum(self._net['throat.'+self._throat_volume_name][i])
#                # Label all invaded pores with their cluster
            # get the throats connecting the boundary pores to the inlet pores, then those are the first filled clusters
#            if sp.in1d(i,bpores):		#if ~sp.in1d(i,bpores): # don't need this if all inlet pores are boundary pores
            bthroat = self._net.find_neighbor_throats(i)  # throat entering inlet pore from boundary pore
            self._Tinv[bthroat] = clusterNumber
            self._Tinv_original[bthroat] = clusterNumber  #self._Pinv_original[i] = clusterNumber
            # Label all boundary-->inlet throats as invaded
            self._tsequence[bthroat] = self._tseq
            if self._timing:
                self._Ttime[bthroat] = self._sim_time
            mask_bpores = sp.vstack([sp.in1d(self._net.find_connected_pores(bthroat)[:,0],i),sp.in1d(self._net.find_connected_pores(bthroat)[:,1],i)])
            interface_pore_numbers = self._net.find_connected_pores(bthroat)[~mask_bpores.T] # i       #self._net.find_connected_pores(np.where(self._Tinv==clusterNumber)[0])
            if self._timing:
                # Sum all interfacial throats' volume coeffients for throat cap volume calculation
                self._cluster_data['vol_coef'][clusterNumber-1] = np.sum(self._Pvol_coef[interface_pore_numbers])  # make -ve because heapq only grabs smallest value, so all Pc are -ve for imbibition
            # Make a list of all entry pressures of the connected pores
            # heapq only allows grabbing the smallest number from the heap, but we need the largest Pcap (smallest pore)
            # python reccomends makign the heap -ve, opping the most negative number, then making it posotive (http://stackoverflow.com/questions/2501457/what-do-i-use-for-a-max-heap-implementation-in-python)
            ''' Pc_entry as -ve (when calculated above)'''
            ''' interface_pore_pressure, heap values, ['haines_pressure'], and ppoints stored as -ve '''
            ''' Pvol_coeff, ['vol_coeff'], ['cap_volume'] are stored as +ve (ie multiply ['haines_pressure'] by -1 when calculating ie ['cap_volume'], etc.)'''
            interface_pore_pressures = Pc_entry[interface_pore_numbers] 
            # Zip pressures and numbers together so that HeapQ can work its magic
            logger.debug('interface pores(s) found:')
            logger.debug(interface_pore_numbers)
            logger.debug( 'interface pore pressure(s):')
            logger.debug(interface_pore_pressures)
            logger.debug( ' Negative Pcap is required for imbibition to work right')
            Interface= list(zip(interface_pore_pressures,interface_pore_numbers))
#            Interface= list(zip([interface_pore_pressures],[interface_pore_numbers]))
            # Turn the zipped throat interfaces object into a heap
            heapq.heapify(Interface)
            # Add to the total list of interface throats in the system
            self._plists.append(interface_pore_numbers.tolist())
            # Add to the total list of invaded interface pores in the system
            self._ppoints.append(Interface)
            # Pop off the first entry (lowest pressure) on the throat info list
            invaded_pore_info = Interface[0]
            if self._timing:
                # Determine pressure at Haines Jump
                self._cluster_data['haines_pressure'][clusterNumber-1] = invaded_pore_info[0]
                # Calculate cap_volume at Haines Jump (need Haines_pressure negative, to recover correct volume)
                self._cluster_data['cap_volume'][clusterNumber-1] = -self._cluster_data['haines_pressure'][clusterNumber-1]*self._cluster_data['vol_coef'][clusterNumber-1]
                # Calculate time at Haines Jump
                self._cluster_data['haines_time'][clusterNumber-1] = (self._cluster_data['throat_volume'][clusterNumber-1]+
                                            self._cluster_data['cap_volume'][clusterNumber-1])/self._cluster_data['flow_rate'][clusterNumber-1]
            # Record invaded throat
            self._cluster_data['haines_pore'][clusterNumber-1] = invaded_pore_info[1]
            clusterNumber += 1
        if self._timing:
            logger.debug( 'throat volumes')
            logger.debug(self._cluster_data['throat_volume'])
            logger.debug( 'cap volumes')
            logger.debug(self._cluster_data['cap_volume'])
            logger.debug( 'max throat cap volumes')
            logger.debug( self._Tvol_coef*self._phase.throat_conditions["Pc_entry"])
        logger.debug( 'haines_pore')
        logger.debug( self._cluster_data['haines_pore'])
#        if self._timing:
#            logger.debug( 'max throat cap volumes')
#            logger.debug( self._Tvol_coef*self._phase.throat_conditions["Pc_entry"])
#        self._tseq += 1
#        self._pseq += 1
        self._current_cluster = 0
        # Calculate the distance between the inlet and outlet pores
        self._outlet_position = np.average(self._net['pore.coords'][self._outlets],0)
        # TODO for calculating the inlet position - should we use distance between invaded pore and outlet, or invading throat?
        # for simplicity for now, using pore coords (averaged anyways)
        inlet_position = np.average(self._net['pore.coords'][self._inlets],0)
        dist_sqrd = (self._outlet_position-inlet_position)*(self._outlet_position-inlet_position)
        self._initial_distance = np.sqrt(dist_sqrd[0]+dist_sqrd[1]+dist_sqrd[2])
        logger.debug( 'initial distance')
        logger.debug( self._initial_distance)
        self._current_distance = self._initial_distance
        self._percent_complete = np.round((self._initial_distance-self._current_distance)/self._initial_distance*100, decimals = 1)
        logger.info( 'percent complete')
        logger.info( self._percent_complete)
        self._rough_complete = 0
        print('     IP algorithm at',np.int(self._rough_complete),'% completion at',np.int(np.round(clock())),'seconds')
        logger.debug( '+='*25)

    def _do_outer_iteration_stage(self):
        r"""
        Executes the outer iteration stage
        """
        logger.info("Outer Iteration Stage ")
        self._pseq = 1
        self._tseq = 1
        self._NewPore = -1
        # Time keeper
        self._sim_time = 0
        self._setup_for_IP()
        self._condition_update()
        #self._Tinv = np.zeros(self._net.num_throats())
        while self._condition:
            self._do_one_outer_iteration()
        self['pore.IP_inv_final']=np.ravel(np.array(self._Pinv,dtype=np.int))
        self['pore.IP_inv_original']=np.ravel(np.array(self._Pinv_original,dtype=np.int))
        self['throat.IP_inv']=np.ravel(np.array(self._Tinv,dtype=np.int))
        self['pore.IP_inv_seq']=np.ravel(np.array(self._psequence,dtype=np.int))
        self['throat.IP_inv_seq']=np.ravel(np.array(self._tsequence,dtype=np.int))
        if self._timing:
            self['pore.IP_inv_time']=np.ravel(np.array(self._Ptime,dtype=np.float))
            self['throat.IP_inv_time']=np.ravel(np.array(self._Ttime,dtype=np.float))

    def _do_one_outer_iteration(self):
        r"""
        One iteration of an outer iteration loop for an algorithm
        (e.g. time or parametric study)
        """
        if (sp.mod(self._counter,500)==False):
            logger.info("Outer Iteration (counter = "+str(self._counter)+")")
            pass
        self._do_inner_iteration_stage()
        self._condition_update()
        self._counter += 1

    def _do_inner_iteration_stage(self):
        r"""
        Executes the inner iteration stage
        """
        logger.debug("  Inner Iteration Stage: ")

        self._plast = len(np.nonzero(self._Pinv)[0])
        if self._timing:
            # determine the cluster with the earliest Haines time
            self._current_cluster = 1 + self._cluster_data['haines_time'].tolist().index(min(self._cluster_data['haines_time']))
            # update simulation clock
            logger.debug( 'sim time = ')
            logger.debug(self._sim_time)
            logger.debug(' haines time:')
            logger.debug( self._cluster_data['haines_time'])
            # The code really messes up when the [0] isn't in the next line. sim_time seems to just point to a place on the haines time array
            self._sim_time = min(self._cluster_data['haines_time'])
            logger.debug( 'sim time after update= ')
            logger.debug(self._sim_time)
        else:
            # Cycle to the next active cluster
            condition = 0
            loop_count = 0
            original_cluster = self._current_cluster
            cnum = original_cluster+1
            while condition == 0:
                if cnum > self._clusterCount:
                    cnum = 1
                if self._cluster_data['active'][cnum-1] == 1:
                    condition = 1
                    self._current_cluster = cnum
                if cnum == original_cluster:
                    loop_count = loop_count+1
                if loop_count > 1:
                    logger.error('No clusters active. Stuck in infinite loop.')
                    pass
                cnum = cnum + 1

        # run through the Haines Jump steps
        self._do_one_inner_iteration()
        self._pnew = len(np.nonzero(self._Pinv)[0])
        self._tseq += 1
        if self._pnew>self._plast:
            self._pseq += 1


    def _do_one_inner_iteration(self):
        r"""
        Executes one inner iteration
        """
        logger.debug("    Inner Iteration")
        # Fill throat and connecting pore
        # Pop out the largest pore (lowest Pcap) in the list, read the pore number
        try:
            pinvade = heapq.heappop(self._ppoints[self._current_cluster-1])[1]
        except:
            print('Something bad happened trying to invade')
            import pdb
#            pdb.set_trace()
        logger.debug( ' ')
        logger.debug( '--------------------------------------------------')
        logger.debug( 'STEP')
        logger.debug(self._tseq)
        logger.debug( 'trying to access cluster: ')
        logger.debug(self._current_cluster)
        logger.debug( 'when these clusters are active active: ')
        logger.debug(sp.nonzero(self._cluster_data['active'])[0])
        logger.debug( 'Haines at pore,time: ')
        logger.debug(pinvade)
        if self._timing:
            logger.debug(self._sim_time)
            pass

        # Mark pore as invaded
        self._psequence[pinvade] = self._pseq
        if self._timing:
            self._Ptime[pinvade] = self._sim_time
            # Remove throat's contribution to the vol_coef
            self._cluster_data['vol_coef'][self._current_cluster-1] = self._cluster_data['vol_coef'][self._current_cluster-1]-self._Pvol_coef[pinvade]
        # Mark throat as filled
        AllThroats = self._net.find_neighbor_throats(pinvade)     # this finds all connected throats, need to ignore the ones that are already filled
        # 1. remove invading throat and any throat already in this cluster (already invaded and part of same cluster)
        Throats = AllThroats[~sp.in1d(AllThroats,np.where(sp.in1d(self._Tinv,self._current_cluster))[0])]
        # 2. fidn other throats with an interface
        # TODO if there is another interface, then start or continue co-operative filling
        # TODO need to add a cooperative filling method
        ThroatsInv = Throats[sp.in1d(Throats,np.where(self._Tinv>0)[0])]
        # if a throat is already invaded (the pore that was just invaded had another interface in it, so now we have cooperative filling)
        # for each already invaded throat
        if len(ThroatsInv):
            # if this pore has multiple interfaces
            self._NewPore = -1
            self._NewThroat = -1
            # Label invaded pore with smallest cluster number
            #   find all clusters connected to the newly invaded pore
            clusters = self._cluster_data['transform'][self._Tinv[AllThroats][self._Tinv[AllThroats]>0]-1]  # clusters = self._cluster_data['transform'][self._Tinv[ThroatsInv]-1]
            logger.debug('clusters = ')
            logger.debug(clusters)
            # if some throats are from different clusters - ie if len(clusters)>1
            if len(clusters)>1:    #if self._Pinv[Pores[0]]!=self._Pinv[Pores[1]] :
                csize = 0
                maxCluster = []
                for c in clusters:  # count occurrences of each value in cluster, in Pinv to find largest cluster
                    if len(self._plists[c-1]) > csize:
                        csize = sum(clusters==c)
                        maxCluster = c
                # find the largest cluster -- FOR IMBIBITION, MERGING ALL SMALLER CLUSTERS INTO THE LARGEST. DIFFERENT FROM DRAININAGE SO BE CAREFUL
                # update the cluster transform to name all clusters as the max
                self._current_cluster = maxCluster   #[0]
                self._Pinv[pinvade] = self._current_cluster
                logger.info(' ')
                logger.info('CLUSTERS COMBINING:')
                logger.info(clusters)
                logger.info('into')
                logger.info(maxCluster)
                if self._timing:
                    logger.info('at time')
                    logger.info(self._sim_time)
                    pass
                for c in clusters[clusters!=self._current_cluster]:  # go through the clusters as they are moved into the largest cluster
                    self._cluster_data['transform'][self._cluster_data['transform']==c] = self._current_cluster
                    # relabel all pores and throats from cluster c to largest
                    self._Pinv[np.where(self._Pinv==c)[0]] = self._current_cluster
                    self._Tinv[np.where(self._Tinv==c)[0]] = self._current_cluster
                    # append the list of throats for the other cluster to the current cluster
                    self._plists[self._current_cluster-1] = self._plists[self._current_cluster-1] + self._plists[c-1]
                    # delete the throat lists on the other cluster
                    self._plists[c-1] = []
                    # merge the heaps of throat information
                    self._ppoints[self._current_cluster-1] = list(heapq.merge(self._ppoints[self._current_cluster-1],self._ppoints[c-1]))
                    if self._timing:
                        # update the clusters' vol_coefs
                        self._cluster_data['vol_coef'][self._current_cluster-1] += self._cluster_data['vol_coef'][c-1]
                        self._cluster_data['vol_coef'][c-1] = 0
                        # update the clusters' pore volume
                        self._cluster_data['throat_volume'][self._current_cluster-1] += self._cluster_data['throat_volume'][c-1]
                        self._cluster_data['throat_volume'][c-1] = 0
                        # update the clusters' flowrates
                        self._cluster_data['flow_rate'][self._current_cluster-1] += self._cluster_data['flow_rate'][c-1]
                        self._cluster_data['flow_rate'][c-1] = 0
                        logger.debug( 'new flowrate for cluster ')
                        logger.debug(self._current_cluster)
                        logger.debug('is')
                        logger.debug(self._cluster_data['flow_rate'][self._current_cluster-1])
                    # check if either was inactive (broke through already)
                    if self._cluster_data['active'][c-1] + self._cluster_data['active'][self._current_cluster-1]<2:
                        logger.debug('making clusters ')
                        logger.debug(c)
                        logger.debug('and')
                        logger.debug(self._current_cluster)
                        logger.debug('inactive due to one being inactive already')
                        logger.debug(self._cluster_data['active'][c-1])
                        logger.debug(self._cluster_data['active'][self._current_cluster-1])
#                        self._cluster_data['active'][self._current_cluster-1] = 0
                        self._cluster_data['active'][c-1] = 0
                        if self._timing:
                            self._cluster_data['haines_time'][c-1] = 100000000000000000000000000000000
                        logger.info(' ')
                        logger.info('CLUSTER MERGED WITH A BREAKTHROUGH CLUSTER')
                    logger.info('making cluster ')
                    logger.info(c)
                    logger.info('inactive due to merge')
                    # update the old cluster's activity and time
                    if self._timing:
                        self._cluster_data['haines_time'][c-1] = 100000000000000000000000000000000
                    self._cluster_data['active'][c-1] = 0
                    # NO IDEA WHAT THIS LINE DOES PLEASE HELP MAHMOUD
                    #self._tpoints[self._current_cluster-1] = list(k for k,v in itertools.groupby(self._tpoints[self._current_cluster-1]))
                    self._ppoints[c-1] = []

        # remove else and do over the length of throats that are not filled:
        # label invaded pore with current cluster
        self._Pinv[pinvade] = self._current_cluster
        self._NewPore = pinvade

        # go through list of new invaded throats and assign to this cluster
        #   first remove all ThroatsInv
        Throats = Throats[~sp.in1d(Throats,ThroatsInv)]
        for i in Throats:
            # set univaded throats, NewThroats
            self._NewThroat = i                 # self._NewPore = Pores[self._Pinv[Pores][:,0]==0][0]
            Pores = self._net.find_connected_pores(i)
            pneighbor = Pores[Pores!=pinvade][0]
            # if it's a boundary throat/pore, print a warning and skip to next i in for loop
            if 'pore.boundary' in self._net.labels(pores=[pneighbor]):
                logger.debug( ' ')
                logger.debug( 'Throat: ')
                logger.debug(self._NewThroat)
                logger.debug('connected to pore: ')
                logger.debug(pneighbor)
                logger.debug(' is a boundary throat. Ignoring and moving on...')
                continue
            logger.debug( ' ')
            logger.debug( 'INVADING THROATS: ')
            logger.debug(self._NewThroat)
            logger.debug('connected to Pore: ')
            logger.debug(pneighbor)
            # label that throat as invaded
            self._Tinv[self._NewThroat] = self._current_cluster
            self._Tinv_original[self._NewThroat] = self._current_cluster
            if self._timing:
                self._Ttime[self._NewThroat] = self._sim_time
            self._tsequence[self._NewThroat] = self._tseq
            if self._timing:
                # update self._cluster_data.['throat_volume']
                self._cluster_data['throat_volume'][self._current_cluster-1] += self._net['throat.'+self._throat_volume_name][self._NewThroat]
            # Get the pore that this throat connects to
            # Update interface list
            # If the pore is not labelled as invaded by the cluster, it must be an interfacial pore
            if (pneighbor not in self._plists[self._current_cluster-1]):      # need extra [] to make a list if only one entry but screw up if multiple entries!!!
                logger.debug( 'new pore:')
                logger.debug(pneighbor)
                logger.debug('connected throats:')
                logger.debug(self._net.find_neighbor_throats(pneighbor))
                # Add this pore data (pressure, number) to this cluster's "heap" of throat data.
                # TODO --> eventually, generalize to capillary_pressure_name
                heapq.heappush(self._ppoints[self._current_cluster-1],(self._phase['pore.Pc_entryImb'][pneighbor],pneighbor))
                # Add new pore number to throat list for this cluster
                # TODO for now, a pore can be in multiple plists (ie not yet invaded, but ready and willing) -- need to watch this
                self._plists[self._current_cluster-1].append(pneighbor)
                if self._timing:
                    # Update the cluster's vol_coef
                    self._cluster_data['vol_coef'][self._current_cluster-1] = self._cluster_data['vol_coef'][self._current_cluster-1]+self._Pvol_coef[pneighbor]
        # Find next Haines Jump info
        # Make sure you are not re-invading a throat
        if self._ppoints[self._current_cluster-1] != []:
            while self._Pinv[self._ppoints[self._current_cluster-1][0][1]] > 0:
                premove = heapq.heappop(self._ppoints[self._current_cluster-1])[1]
                if self._timing:
                    self._cluster_data['vol_coef'][self._current_cluster-1] = self._cluster_data['vol_coef'][self._current_cluster-1]-self._Pvol_coef[premove]
                if self._ppoints[self._current_cluster-1] == []:
                    logger.debug( 'making cluster ')
                    logger.debug(self._current_cluster)
                    logger.debug('inactive due to ppoints = [] ')
                    self._cluster_data['active'][self._current_cluster-1] = 0
                    break
            if self._ppoints[self._current_cluster-1] != []:
                next_pore = self._ppoints[self._current_cluster-1][0][1]
                self._cluster_data['haines_pore'][self._current_cluster-1] = next_pore
                if self._timing:
                    self._cluster_data['haines_pressure'][self._current_cluster-1] = self._ppoints[self._current_cluster-1][0][0]
                    self._cluster_data['cap_volume'][self._current_cluster-1] = self._cluster_data['haines_pressure'][self._current_cluster-1]*self._cluster_data['vol_coef'][self._current_cluster-1]     # PCAP!!

                # Calculate the new Haines jump time
                logger.debug( 'haines time before last stage:')
                logger.debug( self._cluster_data['haines_time'])
        if self._ppoints[self._current_cluster-1] == []:
            logger.debug('making cluster ')
            logger.debug(self._current_cluster)
            logger.debug('inactive due to self._ppoints being empty for that cluster')
            self._cluster_data['active'][self._current_cluster-1] = 0
            if self._timing:
                self._cluster_data['haines_time'][self._current_cluster-1] = 100000000000000000000000000000000
        if self._timing:
            if self._cluster_data['active'][self._current_cluster-1] == 1:
                self._cluster_data['haines_time'][self._current_cluster-1] = (self._cluster_data['throat_volume'][self._current_cluster-1]+self._cluster_data['cap_volume'][self._current_cluster-1])/self._cluster_data['flow_rate'][self._current_cluster-1]
            if self._cluster_data['haines_time'][self._current_cluster-1] < self._sim_time:
                self._cluster_data['haines_time'][self._current_cluster-1] = self._sim_time
            logger.debug('haines time at the end of the pore stuff')
            logger.debug(self._cluster_data['haines_time'])

    def _condition_update(self):
         # Calculate the distance between the new pore and outlet pores
        if self._end_condition == 'breakthrough':
            newpore_position = self._net['pore.coords'][self._NewPore]
            dist_sqrd = (self._outlet_position-newpore_position)*(self._outlet_position-newpore_position)
            if dist_sqrd[0].shape==(3,):     # need to do this for MatFile networks because newpore_position is a nested array, not a vector (?)
                dist_sqrd = dist_sqrd[0]
            newpore_distance = np.sqrt(dist_sqrd[0]+dist_sqrd[1]+dist_sqrd[2])
            logger.debug( 'newpore distance')
            logger.debug( newpore_distance)
            if newpore_distance < self._current_distance:
                self._percent_complete = np.round((self._initial_distance-newpore_distance)/self._initial_distance*100, decimals = 1)
                logger.info( 'percent complete')
                logger.info( self._percent_complete)
                self._current_distance = newpore_distance
        elif self._end_condition == 'total':
            self._percent_complete = np.round((np.sum(self._Pinv>0)/self._net.num_pores())*100, decimals = 1)
        if self._percent_complete > self._rough_complete + self._rough_increment:
            self._rough_complete = np.floor(self._percent_complete/self._rough_increment)*self._rough_increment
            print('     IP algorithm at',np.int(self._rough_complete),'% completion at',np.int(np.round(clock())),'seconds')


        # Determine if a new breakthrough position has occured
        if self._NewPore in self._outlets:
            logger.info( ' ')
            logger.info( 'BREAKTHROUGH AT PORE: ')
            logger.info(self._NewPore)
            logger.info('in cluster ')
            logger.info(self._current_cluster)
            if self._timing:
                logger.info('at time')
                logger.info(self._sim_time)
                pass
            if self._end_condition == 'breakthrough':
                self._cluster_data['active'][self._current_cluster-1] = 0
                if self._timing:
                    self._cluster_data['haines_time'][self._current_cluster-1] = 100000000000000000000000000000000
            elif self._end_condition == 'total':
                self._brkevent.append(self._NewPore)
#        if self._end_condition == 'total':
        if np.sum(self._cluster_data['active']) == 0:
            logger.info( ' ')
            logger.info( 'SIMULATION FINISHED; no more active clusters')
            if self._timing:
                logger.info('at time')
                logger.info(self._sim_time)
                pass
            self._condition = 0
            print('     IP algorithm at 100% completion at ',np.int(np.round(clock())),' seconds')
        # TODO Need to check how total condition will work, and end. All pores or all throats?
#            self._condition = not self._Tinv.all()

    def return_results(self,occupancy='occupancy',IPseq='None'):
        r"""
        """
        if IPseq=='None':
            IPseq = self._pseq

        try:
            self._phase['pore.'+occupancy]=np.ravel(np.array(((self._psequence>0)&(self._psequence<=IPseq)),dtype=np.float))
            self._phase['throat.'+occupancy]=np.ravel(np.array(((self._tsequence>0)&(self._tsequence<=IPseq)),dtype=np.float))
        except:
            print('Something bad happened while trying to update phase',self._phase.name)
        try:
            self._phase_def['pore.'+occupancy]=np.ravel(np.array(~((self._psequence>0)&(self._psequence<=IPseq)),dtype=np.float))
            self._phase_def['throat.'+occupancy]=np.ravel(np.array(~((self._tsequence>0)&(self._tsequence<=IPseq)),dtype=np.float))
        except:
            print('A partner phase has not been set so inverse occupancy cannot be set')

        if IPseq==self._pseq:
            self._phase['pore.IP_inv_final']=np.ravel(np.array(self._Pinv,dtype=np.int))
            self._phase['pore.IP_inv_original']=np.ravel(np.array(self._Pinv_original,dtype=np.int))
            self._phase['throat.IP_inv']=np.ravel(np.array(self._Tinv,dtype=np.int))
            self._phase['pore.IP_inv_seq']=np.ravel(np.array(self._psequence,dtype=np.int))
            self._phase['throat.IP_inv_seq']=np.ravel(np.array(self._tsequence,dtype=np.int))
            if self._timing:
                self._phase['pore.IP_inv_time']=np.ravel(np.array(self._Ptime,dtype=np.float))
                self._phase['throat.IP_inv_time']=np.ravel(np.array(self._Ttime,dtype=np.float))

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)

