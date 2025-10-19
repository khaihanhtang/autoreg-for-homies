import os
import sys
import pytest

from auto_registration_system.model import User
from auto_registration_system.command_handler.handler_new import NewHandler
from auto_registration_system.data_structure.registration_data import RegistrationData
from auto_registration_system.exception.exception_syntax_error import SyntaxErrorException
from config import Config

# Add the parent directory to Python path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(name="admin")
def fixture_admin() -> User:
    """Fixture to provide admin User"""
    return User("admin", "admin_alias", is_admin=True)


@pytest.fixture(name="registration_data")
def fixture_registration_data():
    """Fixture to provide a RegistrationData instance for tests."""
    return RegistrationData()


@pytest.fixture(name="real_main_list")
def fixture_main_list():
    """Fixture to provide a main list content str tests."""
    main_list_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "main_list.txt")
    try:
        with open(main_list_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""


class TestNewHandler:
    """Unit tests for NewHandler class."""

    def test_parse_real_file(self, real_main_list: str, admin: User):
        """Test parsing real main list file content."""
        if not real_main_list:
            # skip this test if main list file is not found or empty
            # we don't want to check in a real file containing real data into version control
            pytest.skip("Main list file not found or empty.")
        test_data = RegistrationData()
        NewHandler.handle(user=admin,
                          message=real_main_list,
                          data=test_data,
                          max_num_players=Config.max_num_players_per_slot)
        assert len(test_data.bookings_by_date_venue) == 7
        # [dv] 🏸14/09 SUN Queenstown cc
        # [s] ❤️1:00-3:00 pm (1), #players: 7
        #   1. Tran Dung
        #   2. Uy(Đem Cầu)
        #   3. Minh Phan
        #   4. James
        #   5. Mr Nguyen
        #   6. Cuong
        #   7. Phong2
        #   reserve. Tuanng(Dem Cầu)
        #   reserve. Trinh
        for x in test_data.bookings_by_date_venue:
            print(f"Date Venue: {x}")
        slot_s = test_data.get_slot("s")
        assert slot_s is not None
        assert len(slot_s.players) == 7
        assert len(slot_s.pending_reservations) == 0
        assert len(slot_s.non_pending_reservations) == 2

    def test_parse_slot_with_owner(self, admin: User):
        """Test parsing slot with owner and payment information."""
        slot_text = """
[dv] 🏸14/09 SUN Queenstown cc
[s] ❤️1:00-3:00 pm (1), #players: 3, owner: Player0
   1. Player1 (pending payment)
   2. Player2 (paid)
   3. Player3
   reserve. Reserve1 (pending)
   reserve. Reserve2
"""
        test_data = RegistrationData()
        NewHandler.handle(user=admin,
                          message=slot_text.strip(),
                          data=test_data,
                          max_num_players=Config.max_num_players_per_slot)

        slot = test_data.get_slot('s')
        assert slot is not None
        assert slot.num_players == 3
        assert slot.owner == "Player0"
        assert slot.is_paid_user("Player1") is False
        assert slot.is_paid_user("Player2") is True
        assert slot.is_paid_user("Player3") is False

        assert "Reserve1" in slot.pending_reservations
        assert "Reserve2" in slot.non_pending_reservations
        
    def test_parse_slot_line_fail(self):
        """Test parsing a slot line with various formats."""
        slot_line = "❤️1:00-3:00 pm (1), #players: 7"

        with pytest.raises(SyntaxErrorException) as excinfo:
            NewHandler.parse_slot_line(slot_line)

    def test_parse_slot_line_standard(self):
        """Test parsing a slot line with various formats."""
        slot_line = "[s] ❤️1:00-3:00 pm (1), #players: 7, owner: @alice"
        slot_detail = NewHandler.parse_slot_line(slot_line)
        assert slot_detail.slot_label == "s"
        assert slot_detail.num_players == 7
        assert slot_detail.owner == "alice"

    def test_parse_slot_line_complex(self):
        """Test parsing a slot line with various formats."""
        slot_line = "[s] ❤️1:00-3:00 pm (1), owner: @alice ,, #players: 7,"
        slot_detail = NewHandler.parse_slot_line(slot_line)
        assert slot_detail.slot_label == "s"
        assert slot_detail.num_players == 7
        assert slot_detail.owner == "alice"

    def test_parse_player_line(self):
        """Test parsing a player line"""

        # line to parse looks something like below
        # 1. Alice (pending payment)
        # 2. Bob (paid)
        # 3. Charlie
        # 4.
        # reserve. David
        alice = NewHandler.parse_player_line("   1. Alice (pending payment)")
        assert alice.name == "Alice"
        assert alice.is_paid is False
        assert alice.is_reserve is False
        assert alice.is_pending is False

        bob = NewHandler.parse_player_line("   2. Bob (paid)")
        assert bob.name == "Bob"
        assert bob.is_paid is True
        assert bob.is_reserve is False
        assert bob.is_pending is False

        charlie = NewHandler.parse_player_line("   3. Charlie")
        assert charlie.name == "Charlie"
        assert charlie.is_paid is False
        assert charlie.is_reserve is False
        assert charlie.is_pending is False

        assert NewHandler.parse_player_line("   4. ") is None

        david = NewHandler.parse_player_line("   reserve. David")
        assert david.name == "David"
        assert david.is_paid is False
        assert david.is_reserve is True
        assert david.is_pending is False

        eva = NewHandler.parse_player_line("   reserve. Eva (pending)")
        assert eva.name == "Eva"
        assert eva.is_paid is False
        assert eva.is_reserve is True
        assert eva.is_pending is True
