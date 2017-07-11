# MARC Tag Use in PCC BSR

I did a quick hack at extracting the MARC tags mentioned in the "MARC ENCODING" column of the Apr 14, 2017 revision of the [PCC-RDA-BSR](https://www.loc.gov/aba/pcc/bibco/documents/PCC-RDA-BSR.pdf) document (code is `marc-bsr-tags-extract.py` in this repo, works from txt saved from Word version of document). Results are:

MARC tags: 007, 008, 020, 024, 033, 034, 040, 041, 042, 043, 045, 046, 048, 050, 052, 074, 088, 130, 1XX, 240, 245, 246, 250, 255, 257, 264, 300, 306, 336, 337, 338, 340, 342, 343, 344, 346, 347, 351, 352, 380, 381, 382, 383, 384, 490, 500, 502, 506, 510, 518, 520, 522, 524, 538, 541, 546, 561, 588, 590, 5XX, 6XX, 7XX, 852, 856, 8XX

MARC tags with sub-fields explicitly mentioned: 040$b, 040$e, 041$d

