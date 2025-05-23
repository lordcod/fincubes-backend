
class State:
    def __init__(self):
        self.current_distance = None
        self.in_relay_block = False
        self.in_team_score_block = False
        self.current_relay_info = None
        self.current_athlete = None
        self.relay_swimmers = []
        self.individual_rows = []
        self.relay_rows = []
        self.relay_team_rows = []
        self.team_score_rows = []
        self.distances = []
