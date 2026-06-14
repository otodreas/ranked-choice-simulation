import uuid

import numpy as np
from numpy.typing import NDArray

np.random.seed(0)

CANDIDATES: dict[str, float] = {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4,
}
N_BALLOTS_CAST: int = 1_000


class Ballot:
    def __init__(self, candidates: dict[str, float]):
        self.valid = True
        self.candidates = list(candidates.keys())

        # Normalize candidate win probabilities
        p_raw = np.array(list(candidates.values()))
        self.candidate_win_probabilities = p_raw / np.sum(p_raw)

    def rank_ballot(self):
        """Simulate an individual vote"""
        self.candidates_ranked = np.random.choice(
            self.candidates,
            np.random.randint(1, len(self.candidates)),
            replace=False,
            p=self.candidate_win_probabilities,
        )

    def get_top_vote(self):
        if len(self.candidates_ranked):
            self.top_vote = self.candidates_ranked[0]
        else:
            self.valid = False

    def remove_top_vote(self):
        self.candidates_ranked = self.candidates_ranked[1:]


class Election:
    def __init__(self):
        self.votes = {}
        self.eliminated_candidates = []

    def submit_ballot(self, ballot: Ballot, voter_id: uuid.UUID):
        self.votes[voter_id] = ballot

    def determine_winner(self):
        self.results = {}
        for ballot in self.votes.values():
            ballot.get_top_vote()
            if ballot.top_vote not in self.results.keys():
                self.results[ballot.top_vote] = 1
            else:
                self.results[ballot.top_vote] += 1

        self.results = {
            candidate: np.float64(n_votes / len(self.votes.values()))
            for candidate, n_votes in self.results.items()
        }
        self.loser = min(self.results, key=self.results.get)
        self.winner = max(self.results, key=self.results.get)
        self.majority_winner = self.results[self.winner] > 0.5

    def rerank(self):
        """Recount votes after the losing candidate has been eliminated"""
        self.eliminated_candidates.append(self.loser)
        discard_voter_ids = []
        for voter_id, ballot in self.votes.items():
            ballot.get_top_vote()

            # Only process ballots whose top choice is the eliminated candidate
            if ballot.top_vote in self.eliminated_candidates:
                ballot.remove_top_vote()
                ballot.get_top_vote()

                # Eliminate 2nd, 3rd choice, and so on if those are also eliminated
                while ballot.top_vote in self.eliminated_candidates and ballot.valid:
                    ballot.remove_top_vote()
                    ballot.get_top_vote()

                # Update top vote or discard ballot if no more votes
                if ballot.valid:
                    self.votes[voter_id] = ballot
                else:
                    discard_voter_ids.append(voter_id)

        for discard_voter_id in discard_voter_ids:
            del self.votes[discard_voter_id]


def simulate_ballot_casting(
    election: Election,
    candidates: NDArray = CANDIDATES,
    n_ballots: int = N_BALLOTS_CAST,
):
    """Simulate the casting of ballots, save voter id"""
    for voter in range(n_ballots):
        ballot = Ballot(candidates)
        ballot.rank_ballot()
        election.submit_ballot(ballot, voter_id=uuid.uuid4())


def print_results(election: Election):
    for candidate, percent in election.results.items():
        print(f"{candidate}: {np.round(percent * 100, 1)}%")


def main():
    # Assign new election
    election = Election()

    # Simulate ballot casting and determine the winner
    print("Starting ranked choice election simulation")
    simulate_ballot_casting(election)
    election.determine_winner()
    
    print("After round 0:")
    print_results(election)
    
    # Start instant runnoff/ranked choice voting until a majority winner is declared
    i = 0
    while not election.majority_winner:
        i += 1
        election.rerank()
        election.determine_winner()

        print(f"Eliminating {election.loser}\nAfter round {i}:")
        print_results(election)

    print(f"Winner: {election.winner} after {i} rounds")


if __name__ == "__main__":
    main()
