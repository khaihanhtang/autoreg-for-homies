import os
import sys

import pytest

from auto_registration_system.model import User
from auto_registration_system.data_structure.slot_manager import SlotManager
from auto_registration_system.exception.exception_name_conflict import \
    NameConflictException

# Add the parent directory to Python path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(name="slot_manager")
def fixture_slot_manager():
    """Fixture to provide a SlotManager instance for tests."""
    return SlotManager("Test Slot", 3)


@pytest.fixture(name="slot_manager_extra")
def fixture_slot_manager_extra():
    """Fixture to provide a SlotManager instance for tests."""
    return SlotManager("Test Slot $3", 3, 3, "owner_user")


@pytest.fixture(name="owner_user")
def fixture_owner_user():
    """Fixture to provide a user that is owner but is not admin"""
    return User("owner_user", "owner_alias", False)


class TestSlotManager:
    """Unit tests for SlotManager class."""

    def test_initialization(self, slot_manager: SlotManager):
        """Test SlotManager initialization."""
        # TODO: Implement test for SlotManager initialization
        assert slot_manager.slot_name == "Test Slot"
        assert slot_manager.num_players == 3
        assert len(slot_manager.players) == 0
        assert len(slot_manager.pending_reservations) == 0
        assert len(slot_manager.non_pending_reservations) == 0

    def test_property_getters(self, slot_manager: SlotManager):
        """Test property getters for slot_name and num_players."""
        # TODO: Implement comprehensive property getter tests
        assert slot_manager.slot_name == "Test Slot"
        assert slot_manager.num_players == 3
        assert isinstance(slot_manager.players, list)
        assert isinstance(slot_manager.pending_reservations, list)
        assert isinstance(slot_manager.non_pending_reservations, list)

    def test_property_setters(self, slot_manager: SlotManager):
        """Test property setters for lists."""
        # TODO: Implement comprehensive property setter tests
        new_players = ["Player1", "Player2"]
        new_pending = ["PendingPlayer"]
        new_non_pending = ["NonPendingPlayer"]

        slot_manager.players = new_players
        slot_manager.pending_reservations = new_pending
        slot_manager.non_pending_reservations = new_non_pending

        assert slot_manager.players == new_players
        assert slot_manager.pending_reservations == new_pending
        assert slot_manager.non_pending_reservations == new_non_pending

    def test_is_in_any_list(self, slot_manager: SlotManager):
        """Test is_in_any_list method."""
        # Test when player is not in any list
        assert not slot_manager.is_in_any_list("NonExistentPlayer")

        # Test when player is in main players list
        slot_manager.players = ["Player1"]
        assert slot_manager.is_in_any_list("Player1")

        # Test when player is in pending reservations
        slot_manager.pending_reservations = ["PendingPlayer"]
        assert slot_manager.is_in_any_list("PendingPlayer")

        # Test when player is in non-pending reservations
        slot_manager.non_pending_reservations = ["NonPendingPlayer"]
        assert slot_manager.is_in_any_list("NonPendingPlayer")

    def test_register_new_player(self, slot_manager: SlotManager):
        """Test registering a new player."""
        # Test registering to main list when space available
        slot_manager.register("Player1")
        assert "Player1" in slot_manager.players
        assert len(slot_manager.players) == 1

    def test_register_when_full(self, slot_manager: SlotManager):
        """Test registering when main list is full."""
        # Fill up main list
        slot_manager.register("Player1")
        slot_manager.register("Player2")
        slot_manager.register("Player3")

        # Register another player (should go to pending)
        slot_manager.register("Player4")
        assert "Player4" in slot_manager.pending_reservations

    def test_register_duplicate_player(self, slot_manager: SlotManager):
        """Test registering a duplicate player raises exception."""
        slot_manager.register("Player1")

        with pytest.raises(NameConflictException):
            slot_manager.register("Player1")

    def test_register_from_non_pending_reservations(self, slot_manager: SlotManager):
        """Test registering a player from non-pending reservations."""
        # TODO: Implement test for moving player from non-pending reservations
        slot_manager.non_pending_reservations = ["ReservedPlayer"]
        slot_manager.register("ReservedPlayer")

        assert "ReservedPlayer" in slot_manager.players
        assert "ReservedPlayer" not in slot_manager.non_pending_reservations

    def test_reserve_player(self, slot_manager: SlotManager):
        """Test reserving a player."""
        slot_manager.register("Player1")
        # Reserving after registering moves player from main to non-pending
        slot_manager.reserve("Player1")
        assert "Player1" not in slot_manager.players
        assert "Player1" in slot_manager.non_pending_reservations

    def test_reserve_pending_player(self, slot_manager: SlotManager):
        """Test reserving a player from pending list."""
        # Fill main list and add pending player
        slot_manager.register("Player1")
        slot_manager.register("Player2")
        slot_manager.register("Player3")
        slot_manager.register("Player4")  # This goes to pending
        slot_manager.reserve("Player4")
        assert "Player4" not in slot_manager.pending_reservations
        assert "Player4" in slot_manager.non_pending_reservations

    def test_restructure(self, slot_manager: SlotManager):
        """Test restructure method."""
        # Set up scenario where restructure should move pending to main
        slot_manager.players = ["Player1", "Player2"]
        slot_manager.pending_reservations = ["PendingPlayer"]
        slot_manager.restructure()
        assert "PendingPlayer" in slot_manager.players
        assert "PendingPlayer" not in slot_manager.pending_reservations
        assert len(slot_manager.players) == 3

    def test_get_num_available(self, slot_manager: SlotManager):
        """Test get_num_available method."""
        # Test when no players registered
        assert slot_manager.get_num_available() == 3

        # Test with some players registered
        slot_manager.register("Player1")
        assert slot_manager.get_num_available() == 2

        # Test when full
        slot_manager.register("Player2")
        slot_manager.register("Player3")
        assert slot_manager.get_num_available() == 0

    def test_to_string(self, slot_manager: SlotManager):
        """Test to_string method."""
        # Test empty slot
        result = slot_manager.to_string("A")
        assert "[A] Test Slot" in result
        assert "#players: 3" in result

        # Test with players
        slot_manager.register("Player1")
        result = slot_manager.to_string("B")

        expected_str = """
[B] Test Slot, #players: 3
   1. Player1
   2.
   3.
"""
        assert result.strip() == expected_str.strip()

    def test_edge_cases(self, slot_manager: SlotManager):
        """Test edge cases and boundary conditions."""
        # TODO: Implement tests for edge cases
        # Test with zero capacity slot
        zero_slot = SlotManager("Zero Slot", 0)
        assert zero_slot.get_num_available() == 0
        # Test with empty strings
        empty_name_slot = SlotManager("", 1)
        assert empty_name_slot.slot_name == ""

    def test_slot_extra_cost(self, slot_manager_extra: SlotManager, owner_user: User):
        """Test registering to a slot with extra payment"""
        slot_manager_extra.register("Player1")
        slot_manager_extra.register("Player2")

        text = slot_manager_extra.to_string("A")
        assert "Player1 (pending payment)" in text
        assert "Player2 (pending payment)" in text

        # Confirm a payment
        assert slot_manager_extra.confirm_payment("Player1", owner_user)
        text = slot_manager_extra.to_string("A")
        assert "Player1 (paid)" in text
        assert "Player2 (pending payment)" in text

        # Confirm payment for user that is already confirmed - nothing changes
        assert not slot_manager_extra.confirm_payment("Player1", owner_user)
        # Confirm payment for user that isn't in the main list
        assert not slot_manager_extra.confirm_payment("Player3", owner_user)

        # assert that nothing changes
        text = slot_manager_extra.to_string("A")
        assert "Player1 (paid)" in text
        assert "Player2 (pending payment)" in text

        # Unconfirm a payment
        assert slot_manager_extra.unconfirm_payment("Player1", owner_user)
        text = slot_manager_extra.to_string("A")
        assert "Player1 (pending payment)" in text
        assert "Player2 (pending payment)" in text

        # Unconfirm non-existing payment
        assert not slot_manager_extra.unconfirm_payment("Player1", owner_user)
        assert not slot_manager_extra.unconfirm_payment("Player3", owner_user)

        text = slot_manager_extra.to_string("A")
        assert "Player1 (pending payment)" in text
        assert "Player2 (pending payment)" in text

    def test_slot_extra_cost_to_string(self, slot_manager_extra: SlotManager, owner_user: User):
        """Test registering to a slot with extra payment"""
        slot_manager_extra.register("Player1")
        slot_manager_extra.register("Player2")
        expected_str = """
[A] Test Slot $3, #players: 3
   1. Player1 (pending payment)
   2. Player2 (pending payment)
   3.
"""
        assert slot_manager_extra.to_string("A").strip() == expected_str.strip()


@pytest.fixture
def integration_slot_manager():
    """Fixture to provide a SlotManager instance for integration tests."""
    return SlotManager("Integration Test Slot", 2)


class TestSlotManagerIntegration:
    """Integration tests for SlotManager with multiple operations."""

    def test_complete_workflow(self, integration_slot_manager: SlotManager):
        """Test complete workflow of registration, reservation, etc."""
        # Register players until full
        integration_slot_manager.register("Player1")
        integration_slot_manager.register("Player2")
        integration_slot_manager.register("Player3")  # Should go to pending

        # Reserve a main player
        integration_slot_manager.reserve("Player1")

        # Verify restructuring happened
        assert "Player3" in integration_slot_manager.players
        assert "Player1" in integration_slot_manager.non_pending_reservations
        assert len(integration_slot_manager.pending_reservations) == 0
