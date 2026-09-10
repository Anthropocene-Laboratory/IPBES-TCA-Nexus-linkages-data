# Expert-coded linkages between IPBES transformative-change actions and Nexus response options

[![Licence: CC BY 4.0](https://img.shields.io/badge/Licence-CC%20BY%204.0-lightgrey.svg)](./LICENSE)

1,692 judgements by eight IPBES expert authors, each linking one of the **22 transformative-change
actions** of the IPBES Transformative Change Assessment (chapter 5) to one of the **71 response
options** of the IPBES Nexus Assessment (chapter 5), and qualifying the linkage as *primary* or
*secondary*.

This is the minimal dataset behind the accompanying article. Every number reported there is
recomputed from these files and nothing else:

```bash
python verify.py
```

Eighteen checks, from the headline counts down to the concentration statistics of the results
section. If one fails, the dataset and the article disagree and the article is the one to doubt.

## Files

| File | Rows | What it is |
|---|---|---|
| `linkages.csv` | 1,692 | one row per expert judgement |
| `tca_actions.csv` | 22 | the actions, with their strategy and published wording |
| `nexus_response_options.csv` | 71 | the response options, with their category and title |
| `verify.py` | — | recomputes the article's numbers from the three files above |

### `linkages.csv`

| Column | Values | Meaning |
|---|---|---|
| `coder` | eight of `Coder A`…`Coder N` | who made the judgement. Labels come from a project-wide assignment covering everyone who ever registered, so the eight present here are not a contiguous run; the gaps are registrations that produced no judgement. The same label denotes the same person in every file and every analysis output. |
| `tca_action_id` | `TCA5-A01` … `TCA5-A22` | the action, keyed to `tca_actions.csv` |
| `nexus_option_id` | e.g. `B14`, `F16`, `B03; C11` | the response option, keyed to `nexus_response_options.csv`. Four options carry compound identifiers (`B03; C11`, `B02; C14`, `F03; C02`, `F11; C15`) because the assessment itself lists them under two numbers. |
| `strength` | `primary` or `secondary` | whether the coder judged the option a principal means of delivering the action, or a complementary one |

Rows are independent judgements, never merged: two coders who identify the same pair produce two
rows, and they may disagree on strength. That is deliberate — consensus and divergence are both
recoverable, and the article's agreement threshold (a pair counts when at least two coders
identify it) is applied at analysis time, not at collection time.

## How the data were produced

Judgements were elicited with the **TCA-Nexus Linker**
([source](https://github.com/Anthropocene-Laboratory/IPBES-TCA-Nexus-Linker)), a web application
built for this study. It is an elicitation instrument, not an inference tool: it proposes no
candidate matches, ranks nothing, and computes no textual similarity. Coders saw the two lists
side by side with the verbatim published definitions, and every recorded link is an explicit
judgement.

The dataset is exported from the application's database by
[`scripts/export-dataset.cjs`](https://github.com/Anthropocene-Laboratory/IPBES-TCA-Nexus-Linker/blob/main/scripts/export-dataset.cjs)
in that repository, which is also what applies the pseudonyms.

## What is not here, and why

**Coder identities.** The eight experts are acknowledged in the article; which of them made which
judgement is not published. Pseudonyms are assigned in the order of the SHA-256 digest of the
name, so the labels disclose neither the coders' volumes nor their initials, and the mapping is
kept in a private repository.

**Names, e-mail addresses, timestamps, database row identifiers, and the 66 free-text remarks
coders attached to individual links.** None is needed to reproduce a published result, and each is
either personal or an artefact of collection. The remarks are held back rather than discarded:
they are unstructured, unprompted and unreviewed, and releasing them would mean reading all 66
for identifying content first.

Everything the article reports is nonetheless recomputable, including the per-coder analyses:
agreement, leave-one-coder-out robustness and coder effort all work from the pseudonyms.

## Citing

Cite the dataset by its DOI, not by this URL — a repository link is not a persistent identifier.
The DOI is minted on release through Zenodo and will appear here and in the accompanying
article's data availability statement.

## Licence

[CC BY 4.0](./LICENSE). The IPBES definitions reproduced in the two reference files remain the
property of IPBES and are included with attribution; their reuse is governed by IPBES's terms.
