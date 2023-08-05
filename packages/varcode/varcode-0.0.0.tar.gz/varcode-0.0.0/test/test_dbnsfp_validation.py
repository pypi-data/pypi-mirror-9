# Copyright (c) 2014. Mount Sinai School of Medicine
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pandas as pd
from varcode import VariantAnnotator, Substitution, Variant

annot = VariantAnnotator(75)

def validate_transcript_mutation(
	ensembl_transcript,
        chrom, dna_position,
        dna_ref, dna_alt,
        aa_pos, aa_alt):
    result = annot.describe_variant(
        Variant(chrom, dna_position, dna_ref, dna_alt))
    assert ensembl_transcript in result.transcript_effects, \
        "%s not found in %s" % (ensembl_transcript, result)
    effect = result.transcript_effects[ensembl_transcript]
    assert (
        isinstance(effect, Substitution) and
        effect.aa_pos + 1 == aa_pos and
        effect.mutant_protein_sequence[effect.aa_pos] == aa_alt
    ), "Mutation p.%d%s not found for mutation chr%s:%s %s>%s : %s" % (
        aa_pos, aa_alt,
        chrom, dna_position,
        dna_ref, dna_alt, effect)

def test_dbnsfp_validation_set():
    # check that amino acid substitution gives
    # same answer as subset of dbNSFP entries (using Ensembl 75)

    # columns for validation dataset:
    # - aa_pos : base-1 position within protein
    # - dna_alt : non-reference DNA nucleotide
    # - chrom : choromosome
    # - ensembl_transcript : transcript ID
    # - dna_position : base-1 position within chromosome
    # - dna_ref : reference DNA nucleotide
    validation_set = pd.read_csv('dbnsfp_validation_set.csv')
    for _, row in validation_set.iterrows():
        args = (
	    row['ensembl_transcript'],
            row['chrom'],
            row['dna_position'],
            row['dna_ref'],
            row['dna_alt'],
            row['aa_pos'],
            row['aa_alt']
        )
        # making this a generator so every row shows up as its
        # owns test in nose
        yield (validate_transcript_mutation,) + args

if __name__ == '__main__':
    for test_tuple in test_dbnsfp_validation_set():
        f = test_tuple[0]
	args = test_tuple[1:]
	f(*args)
