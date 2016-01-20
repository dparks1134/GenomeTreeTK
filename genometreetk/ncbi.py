###############################################################################
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program. If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

import csv

"""Functions for working with NCBI genomes and metadata."""


def read_genome_dir(genome_dir_file):
    """Parse genome dir file.

    """

    genome_dirs = {}
    for line in open(genome_dir_file):
        line_split = line.rstrip().split('\t')
        genome_dirs[line_split[0]] = line_split[1]

    return genome_dirs


def read_refseq_metadata(metadata_file, keep_db_prefix=False):
    """Parse metadata for RefSeq genomes from GTDB metadata file.

    Parameters
    ----------
    metadata_file : str
        File specifying metadata for all genomes.

    Returns
    -------
    dict : d[assembly_accession] -> taxonomy id
        Taxonomy id of assemblies.
    set
        Set of complete genomes based on NCBI assembly level.
    set
        Set of reference or representative genomes based on NCBI RefSeq category.
    """

    accession_to_taxid = {}
    complete_genomes = set()
    representative_genomes = set()

    csv_reader = csv.reader(open(metadata_file, 'rt'))
    bHeader = True
    for row in csv_reader:
        if bHeader:
            genome_index = row.index('genome')
            taxid_index = row.index('ncbi_taxid')
            assembly_level_index = row.index('ncbi_assembly_level')
            refseq_category_index = row.index('ncbi_refseq_category')
            bHeader = False
        else:
            assembly_accession = row[genome_index]
            if assembly_accession.startswith('RS_'):
                if not keep_db_prefix:
                    assembly_accession = assembly_accession.replace('RS_', '').replace('GB_', '')

                accession_to_taxid[assembly_accession] = row[taxid_index]

                assembly_level = row[assembly_level_index].lower()
                if assembly_level == 'complete genome':
                    complete_genomes.add(assembly_accession)

                refseq_category = row[refseq_category_index].lower()
                if 'reference' in refseq_category or 'representative' in refseq_category:
                    representative_genomes.add(assembly_accession)

    return accession_to_taxid, complete_genomes, representative_genomes


def read_type_strains(type_strain_file):
    """Parse type strain file.

    Parameters
    ----------
    type_strain_file : str
        File specifying NCBI taxonomy identifiers representing type strains.

    Returns
    -------
    set
        NCBI taxonomy identifiers of type strains.
    """

    type_strain_taxids = set()
    with open(type_strain_file) as f:
        for line in f:
            line_split = line.split('\t')
            type_strain_taxids.add(line_split[0])

    return type_strain_taxids


def get_type_strains(genome_ids, accession_to_taxid, type_strain_taxids):
    """Get genomes representing a type strain.

    Parameters
    ----------
    genome_ids : set
        Genomes to check.
    accession_to_taxid : d[assembly_accession] -> taxonomy id
        NCBI taxonomy identifier for each genomes.
    type_strain_taxids : set
        NCBI taxonomy identifiers of type strains.

    Returns
    -------
    set
        Genomes representing a type strain.
    """

    type_strains = set()
    for genome_id in genome_ids:
        taxid = accession_to_taxid.get(genome_id, -1)

        if taxid in type_strain_taxids:
            type_strains.add(genome_id)

    return type_strains
