import numpy as np

np.random.seed(0)

CANDIDATES = np.array(["A", "B", "C", "D"])
N_BALLOTS: int = 1_000


class Ballot:
    def __init__(self, candidates):
        self.candidates = candidates

    def rank_ballot(self):
        self.candidates_ranked = np.random.choice(
            self.candidates,
            np.random.randint(1, len(self.candidates)),
            replace=False,
        )

    def update_top_vote(self):
        # TODO: handle missing ranking
        self.top_vote = self.candidates_ranked[0]

    def remove_top_vote(self):
        self.candidates_ranked = self.candidates_ranked[1:]


def simulate_ballot_casting(
    candidates: np.array = CANDIDATES, n_ballots: int = N_BALLOTS
) -> list[Ballot]:
    voters = np.arange(n_ballots)
    ballots = []
    for v in voters:
        ballot = Ballot(candidates)
        ballot.rank_ballot()
        ballots.append(ballot)

    return ballots


def tabulate_votes(ballots: list[Ballot]) -> dict[np.str_, np.float64]:
    results = {}
    for b in ballots:
        b.update_top_vote()
        if b.top_vote in results.keys():
            results[b.top_vote] += 1 / len(ballots)
        else:
            results[b.top_vote] = 1 / len(ballots)

    return results


def main():
    ballots = simulate_ballot_casting()
    results = tabulate_votes(ballots)


if __name__ == "__main__":
    main()
