"""
All reports assume the _set pickle from snp is given, the
taxonomy and some filtering/output option

General report:

* gene count per sample, using desired coverage (default 4x)
* barchart with eggnog categories per taxa (order, genus, phylum - default)
* barchart proportions eggnog categories per taxa (order, genus, phylum - default)
* boxplot of taxa variation (order, genus, phylum - default)
* table with gene count with mappings - top 20 (.csv imported in rst file)
* histogram coverage per sample (excluding 0x)
* table number of genes per sample
* table number of reads

Gene report:

* boxplot all genes
* boxplot for all genes in pathways
* boxplot for each genes

category report:

* one report file per mapping
* boxplot of variation
* boxplot per all taxa (at desired level), but only include in the rst file the
  top 10 at most

Taxon report:

* boxplot for gene variation
* boxplot pathway variation
* eggnog categories

two way comparison:

* test common genes
* venn diagram
* pie chart
* per pathway
* boxplot significant genes
* overrepresentation test?
* provide file to use in kegg

three way comparison:

* test common genes (3 comparisons)
* venn diagram
* pie chart
* per pathway
* boxplot significant genes
* provide file to use in kegg

* make a rst text file with relative figures for conversion into PDF if rst2pdf
  or rst2html is installed
"""
