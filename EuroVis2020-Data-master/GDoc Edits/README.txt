The revision history for the notes each reservist took during the experiment, organizes as
a series of directories. 

Each directory file contains the full revision history of the notes
one reservist took while participating in the experiment. Within the directory, the first 
file (typically empty), represents the first recorded state of the document, while the
rest of the files in the directory (*.patch) represent the changes that were made between each
timestamp (typically a few minutes) that Google recorded a revision for, 
in the format of the output of the diff command 
(lines added are prefixed with +, lines removed with -, and several lines of 
context are given on each side of a change). The full text of the document at a given 
time can be reconstructed by running the patch command on the initial file and each
subsequent patch file. 

For example, to reconstruct the full text at time step 2:
$ patch VAST*_revision_0_* VAST*_revision_1_*.patch
$ patch VAST*_revision_0_* VAST*_revision_2_*.patch


Additional notes for the revision histories:
- These were obtained by automating a web browser to pull the full text from each
document at each timestamp (literally opening the Google Docs revision tab and
going through each revision). Often, a particular revision will include a few words
that are being removed at that time.
- User VASTOMS took notes in a Google Sheets book instead of in Google Docs. Each
sheet in the spreadsheet is prefixed with --- Sheetname --- in the resulting text.
- User VASTL6X took notes in two separate documents, and therefore have entries under
VASTL6X_1 and VASTL6X_2