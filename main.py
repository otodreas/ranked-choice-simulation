import uuid

import numpy as np

np.random.seed(0)

CANDIDATES = np.array(["A", "B", "C", "D"])
N_BALLOTS: int = 1_000


class Ballot:
    def __init__(self, candidates):
        self.candidates = candidates
        self.valid = True

    def rank_ballot(self):
        self.candidates_ranked = np.random.choice(
            self.candidates,
            np.random.randint(1, len(self.candidates)),
            replace=False,
        )

    def get_top_vote(self):
        # TODO: handle missing ranking
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
        for ballot in self.votes.values():  # TODO: handle missing ballots
            ballot.get_top_vote()
            if ballot.top_vote not in self.results.keys():
                self.results[ballot.top_vote] = 1
            else:
                self.results[ballot.top_vote] += 1

        self.results = {
            candidate: n_votes / len(self.votes.values())
            for candidate, n_votes in self.results.items()
        }
        self.loser = min(self.results, key=self.results.get)
        self.winner = max(self.results, key=self.results.get)
        self.majority_winner = self.results[self.winner] > 0.5

    def rerank(self):
        self.eliminated_candidates.append(self.loser)
        discard_voter_ids = []
        for voter_id, ballot in self.votes.items():
            ballot.get_top_vote()
            if ballot.top_vote in self.eliminated_candidates:
                ballot.remove_top_vote()
                ballot.get_top_vote()
                while (
                    ballot.top_vote in self.eliminated_candidates
                    and ballot.valid == True
                ):
                    ballot.remove_top_vote()
                    ballot.get_top_vote()
                if ballot.valid == True:
                    self.votes[voter_id] = ballot
                else:
                    discard_voter_ids.append(voter_id)

        for discard_voter_id in discard_voter_ids:
            del self.votes[discard_voter_id]


def simulate_ballot_casting(
    election: Election, candidates: np.array = CANDIDATES, n_ballots: int = N_BALLOTS
):
    for voter in range(n_ballots):
        ballot = Ballot(candidates)
        ballot.rank_ballot()
        election.submit_ballot(ballot, voter_id=uuid.uuid4())


def main():
    election = Election()
    simulate_ballot_casting(election)
    election.determine_winner()
    while not election.majority_winner:
        election.rerank()
        election.determine_winner()

    return election.winner


if __name__ == "__main__":
    main()
