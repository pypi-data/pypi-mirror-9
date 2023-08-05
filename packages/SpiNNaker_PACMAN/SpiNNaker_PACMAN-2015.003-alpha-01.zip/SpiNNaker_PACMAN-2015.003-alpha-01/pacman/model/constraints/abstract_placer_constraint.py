from abc import ABCMeta
from abc import abstractmethod
from six import add_metaclass

from pacman.model.constraints.abstract_constraint import AbstractConstraint


@add_metaclass(ABCMeta)
class AbstractPlacerConstraint(AbstractConstraint):
    """ A constraint that will be used by the placer
    """

    def __init__(self, label):
        AbstractConstraint.__init__(self, label)

    def is_constraint(self):
        return True

    @abstractmethod
    def is_placer_constraint(self):
        """ Determine if this is a placer constraint
        """
        pass

    @abstractmethod
    def rank(self):
        """property method for all placer constraints to have for sorting
        :return: the importance of this constraint over others in the same \
        catergory
        :rtype: int between 0 and sys.maxint.
        :raise None: does not raise any known exception
        """
