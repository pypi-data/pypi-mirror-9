import logging

from pacman.model.constraints.abstract_constraints.\
    abstract_placer_constraint import \
    AbstractPlacerConstraint
from pacman.operations.abstract_algorithms.\
    abstract_placer_algorithm import\
    AbstractPlacerAlgorithm
from pacman.model.constraints.placer_constraints.\
    placer_chip_and_core_constraint \
    import PlacerChipAndCoreConstraint
from pacman.model.placements.placements import Placements
from pacman.model.placements.placement import Placement
from pacman.utilities import utility_calls
from pacman.utilities.progress_bar import ProgressBar
from pacman.utilities.resource_tracker import ResourceTracker


logger = logging.getLogger(__name__)


class BasicPlacer(AbstractPlacerAlgorithm):
    """ A basic placement algorithm that can place a partitioned_graph onto\
        a machine using the chips as they appear in the machine
    """

    def __init__(self):
        """

        :param machine: The machine on which the placement will take place
        :type machine: :py:class:`spinn_machine.machine.Machine`
        """
        AbstractPlacerAlgorithm.__init__(self)

        self._supported_constraints.append(PlacerChipAndCoreConstraint)

    def place(self, partitioned_graph, machine):
        """ Place a partitioned_graph so that each subvertex is placed on a\
                    core

        :param partitioned_graph: The partitioned_graph to place
        :type partitioned_graph:\
                    :py:class:`pacman.model.partitioned_graph.partitioned_graph.PartitionedGraph`
        :return: A set of placements
        :rtype: :py:class:`pacman.model.placements.placements.Placements`
        :raise pacman.exceptions.PacmanPlaceException: If something\
                   goes wrong with the placement
        """

        # check that the algorithm can handle the constraints
        utility_calls.check_algorithm_can_support_constraints(
            constrained_vertices=partitioned_graph.subvertices,
            supported_constraints=self._supported_constraints,
            abstract_constraint_type=AbstractPlacerConstraint)

        placements = Placements()
        ordered_subverts = utility_calls.sort_objects_by_constraint_authority(
            partitioned_graph.subvertices)

        # Iterate over subvertices and generate placements
        progress_bar = ProgressBar(len(ordered_subverts),
                                   "for placing the partitioned_graphs "
                                   "subvertices")
        resource_tracker = ResourceTracker(machine)
        for subvertex in ordered_subverts:

            # Create and store a new placement anywhere on the board
            (x, y, p, _, _) = resource_tracker.allocate_constrained_resources(
                subvertex.resources_required, subvertex.constraints)
            placement = Placement(subvertex, x, y, p)
            placements.add_placement(placement)
            progress_bar.update()
        progress_bar.end()
        return placements
