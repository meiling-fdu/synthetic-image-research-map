# Maintenance Backlog

This document groups current maintenance work by purpose. Paper-specific correction evidence and status live in `data/manual/correction_backlog.csv`; confirmed export overrides remain in their dedicated manual override tables. Backlog entries are review records, not automatic corrections.

## Confirmed Institution Corrections

- Keep the RMIT University, Washington State University, and Queensland University of Technology replacement for *Generative Visual AI in News Organizations* as a regression case; MIT University in Skopje must not return.
- Add Ant Group to *WildFake* using the official author mapping once a local verified location record is available. Do not invent coordinates.
- Preserve the Indian Institute of Engineering Science and Technology correction for *Leveraging Image Gradients for Robust GAN-Generated Image Detection in OSN context*.
- Preserve the three-institution replacement for *Discovering Transferable Forensic Features for CNN-Generated Images Detection*.
- Preserve Michael Albright and Scott McCloskey as the Honeywell authors for *Source Generator Attribution via Inversion*.

## Suspected Institution Corrections

- Review the suspicious Institute of Art and National Science Centre records for *DIRE for Diffusion-Generated Image Detection*.
- Review the SRM/Dhanekula, Karnatak/University of Chakwal, Brandman/Reichman, and Graphic Era/Graphic Era Hill conflicts recorded in the correction backlog.
- Reconstruct the full affiliation mapping for *Detecting GAN generated Fake Images using Co-occurrence Matrices*. Treat China Lake as a California place name, not country evidence.
- Do not promote suspected corrections directly into `institution_record_overrides.csv`; verify full-paper author coverage and local coordinates first.

## Scope / Exclusion Review

- Review *Generative Visual AI in News Organizations: Challenges, Opportunities, Perceptions, and Policies* against the project boundary. It may be primarily about news practice, policy, and perceptions rather than synthetic-image detection or source attribution.

## Frontend Bugs

- External-link controls must be conditional. Paper, DOI, arXiv, and OpenAlex links should appear only when their corresponding metadata resolves to a usable absolute HTTP(S) URL.
- Keep missing-link behavior as a regression check: no empty link, `href="#"`, malformed URL, or missing arXiv metadata may navigate back to or refresh the current page.

## Future Feature Backlog

- Show the original paper abstract in Paper details.
- Support an AI-generated paper summary, clearly separated and labeled apart from the original abstract.
- Add a link-based paper importer.
- Add a PDF-based paper importer.
- Build a human-in-the-loop candidate review workflow.
- Establish a weekly Google Scholar Alert review workflow.
- Add an institution-level collaboration view.
- Encode institution paper count through marker color intensity.
- Build a raw-affiliation-first institution pipeline with ROR normalization and manual overrides.
