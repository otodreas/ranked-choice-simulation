import uuid

import numpy as np
from numpy.typing import NDArray

np.random.seed(42)

# Build a square matrix of win probability per rank position
CANDIDATES: dict[str, list[float]] = {
    "A": [4, 1, 1, 1],
    "B": [2, 1, 1, 1],
    "C": [2, 1, 1, 1],
    "D": [3, 5, 6, 5],
}
N_BALLOTS_CAST: int = 1_000


class Ballot:
    """One ballot"""

    def __init__(self, candidates: dict[str, list[float]]):
        self.valid = True
        self.candidates = list(candidates.keys())

        # Normalize candidate win probabilities
        p_raw = np.array(list(candidates.values()))
        self.candidate_win_probabilities = p_raw / np.sum(p_raw, axis=0)

    def rank_ballot(self):
        """Simulate an individual vote, with unique probabilities for each round"""

        # Assign global variables
        self.candidates_ranked = []

        # Assign local variables to be iterated over for each round of selection
        n_candidates_ranked = np.random.randint(1, len(self.candidates) + 1)
        available_candidates = self.candidates
        p_local = self.candidate_win_probabilities

        for c in range(n_candidates_ranked):
            # Select candidate based on probability at a given rank (2nd, 3rd place, etc.)
            candidate_chosen = np.random.choice(
                available_candidates,
                replace=False,
                p=p_local[:, c],
            )

            # Update globals
            self.candidates_ranked.append(candidate_chosen)

            # Update locals: remove chosen candidate from available candidates. Remove corresponding row and re-normalize probability matrix
            chosen_candidate_index = available_candidates.index(candidate_chosen)
            available_candidates.pop(chosen_candidate_index)

            p_local = np.delete(p_local, chosen_candidate_index, axis=0)
            p_local = p_local / np.sum(p_local, axis=0)

    def get_top_vote(self):
        if len(self.candidates_ranked):
            self.top_vote = self.candidates_ranked[0]
        else:
            self.valid = False

    def remove_top_vote(self):
        self.candidates_ranked = self.candidates_ranked[1:]


class Election:
    """One election, made up of many :Ballot: objects, each cast by a unique voter"""

    def __init__(self, candidates: dict[str, list[float]] = CANDIDATES, n_ballots: int = N_BALLOTS_CAST):
        self.candidates = candidates
        self.n_ballots = n_ballots
        self.votes = {}
        self.eliminated_candidates = []

    def simulate_ballot_casting(self):
        """Simulate the casting of ballots, save voter id"""
        for voter in range(self.n_ballots):
            ballot = Ballot(self.candidates)
            ballot.rank_ballot()
            self.votes[uuid.uuid4()] = ballot

    def determine_winner(self):
        """Determine winner of election. Meant to be run iteratively following runoff"""

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

    def runoff(self):
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

    def print_results(self, preamble: str):
        print(preamble)
        for candidate, percent in self.results.items():
            print(f"{candidate}: {np.round(percent * 100, 1)}%")


def main():
    # Assign new election
    election = Election()

    # Simulate ballot casting and determine the winner
    print("Starting ranked choice election simulation")
    election.simulate_ballot_casting()
    election.determine_winner()

    election.print_results("After initial count:")

    # Start instant runnoff/ranked choice voting until a majority winner is declared
    i = 0
    while not election.majority_winner:
        i += 1
        election.runoff()
        election.determine_winner()

        election.print_results(f"After round {i}:")

    print(f"Winner: {election.winner} after {i} rounds")


if __name__ == "__main__":
    main()
