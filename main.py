import numpy as np


CANDIDATES = np.array(["A", "B", "C", "D"])
N_BALLOTS: int = 1_000

class Ballot():
    def __init__(self):
        pass

    def rank_ballot(self, candidates):
        np.random.shuffle(candidates)
        self.candidates_ranked = candidates[: np.random.randint(1, len(candidates) + 1)]
        

def simulate_ballot_casting(candidates: np.array = CANDIDATES, n_ballots: int = N_BALLOTS) -> dict[np.int64, np.array]:
    voters = np.arange(n_ballots)
    ballots = {}
    for v in voters:
        ballot = Ballot()
        ballot.rank_ballot(candidates.copy())
        ballots[v] = ballot

    return ballots


def main():
    ballots = simulate_ballot_casting()
    

if __name__ == "__main__":
    main()
