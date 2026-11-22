# Winnow

**Finds which Wikipedia articles a text was copied from, and marks the copied passages.**

You give Winnow a document. It searches millions of Wikipedia articles, returns the likely sources, and marks each reused passage (as character ranges in both texts) with a score for how likely it is real reuse rather than coincidence.

It is a small, from-scratch take on the problem that plagiarism and content-reuse detectors solve: search at scale, exact alignment, and a classifier on top.

> Status: planning done, implementation starting (milestone M0).

## How this project is built

This is a learning project, and the rule is simple: **I write all of the code and logic myself.**

An AI assistant (Claude) is used as a mentor, not as an author:

- **Planning:** it helped frame the problem, choose the data and design the milestones and evaluation plan.
- **Teaching:** it explains algorithms, data structures and trade-offs, and answers questions.
- **Reviewing:** it reads my code and points out bugs, edge cases and simpler designs. I make the fixes.

It does not write the implementation: no index, no winnowing, no alignment, no classifier, no C code. There are two exceptions, both plumbing that Claude wrote at my request:

- the first commit (dev container, requirements, `.gitignore` and this README), which is environment setup;
- `winnow/wikidump.py`, which streams `(id, title, raw wikitext)` out of the Wikipedia XML dump. Cleaning that wikitext into plain text is my own code.

Libraries are used only for plumbing (arrays, file formats, AWS access) and to check my own implementations against a reference, never in place of them.

## How it works

Three steps, like a detective: find suspects, compare the evidence, give a verdict.

```
                     Index, built once (Wikipedia + PAN sources)
                                   |
Suspicious document --> 1. Find suspects --> 2. Compare evidence --> 3. Verdict --> Report
                        winnowing index      seed, extend, merge      classifier:    ranked sources +
                        ~6M articles -> ~50  into copied passages     reuse or       highlighted passages
                                                                      coincidence?
```

1. **Find suspects.** An inverted index of winnowing fingerprints narrows millions of articles down to a few dozen candidates. (MinHash/LSH is built too, as a comparison.)
2. **Compare evidence.** Matching fingerprints are used as seeds, extended into longer matches and merged into passages.
3. **Verdict.** A hand-written classifier decides, per passage, whether it is real reuse or a coincidence (common phrases, quotes, shared topic), using features such as match length, word rarity, density and order.

## Data

| Piece | Role |
| --- | --- |
| English Wikipedia dump | The haystack: millions of articles to search |
| PAN plagiarism corpora | Human-made test cases with every copied passage marked; their source documents are added to the haystack |
| Generated set | Wikipedia passages, changed by simple rules and planted into other text, so the answer is known; any size |

Data is downloaded into `data/`, which is not committed.

## Evaluation

Each step is measured separately, so a bad result points at the step that caused it.

| Step | Metric |
| --- | --- |
| Find suspects | Recall@10, recall@50: is the true source among the candidates? |
| Compare evidence | PAN character-level precision, recall, granularity and plagdet |
| Verdict | Precision, recall and F1 on the reuse class, PR curve |
| Whole system | Seconds per document, index size, AWS cost per month |

Train and test sets are split by source article, so no article appears on both sides. Every number is reported next to a simple baseline.

## Milestones

- [ ] **M0 Data:** PAN, a 10,000-article Wikipedia slice, my own markup cleaner, the test-case generator
- [ ] **M1 Baseline:** brute-force comparison on the small slice, the numbers to beat
- [ ] **M2 Find suspects:** inverted index (TF-IDF/BM25) and winnowing fingerprint index
- [ ] **M3 Compare evidence:** seed, extend and merge passages; PAN score
- [ ] **M4 Verdict:** passage features and a hand-written logistic regression
- [ ] **M5 Scale and C:** full Wikipedia, sharded index, C library for hashing and fingerprints
- [ ] **M6 AWS:** index in S3, batch build on spot machines, query API, all in Terraform
- [ ] **M7 Stretch:** scan a Common Crawl sample for pages that copy Wikipedia

Out of scope for now: translated copies, heavy paraphrase, neural embeddings, crawling the live web.

## Development environment

The repo includes a dev container, so it opens ready to work in GitHub Codespaces (2 cores and 8 GB RAM are enough up to M4) or in VS Code with Docker.

It installs:

- Python 3.12 with the packages in `requirements.txt`
- gcc, make, gdb and valgrind for the C library
- `/usr/bin/time` and `pv` for measuring memory and following long runs
- Terraform and the AWS CLI for M6

Check it after the container starts:

```bash
python --version && gcc --version && terraform -version && aws --version
```
