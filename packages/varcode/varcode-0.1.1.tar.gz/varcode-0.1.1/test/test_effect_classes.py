# Copyright (c) 2015. Mount Sinai School of Medicine
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
The different effects get tested in an ad-hoc manner throughout the
unit test but the goal of this test module is to make sure that there is
at least one test for each effect class
"""

from varcode import (
    Variant,
    #
    # transcript effects
    #
    IncompleteTranscript,
    NoncodingTranscript,
    FivePrimeUTR,
    ThreePrimeUTR,
    Intronic,
    Silent,
    Insertion,
    Deletion,
    Substitution,
    StopLoss,
    StartLoss,
    AlternateStartCodon,
    PrematureStop,
    FrameShift,
    ExonLoss,
    ExonicSpliceSite,
    # TODO: SpliceDonor, SpliceReceptor
)
from pyensembl import EnsemblRelease

ensembl_grch37 = EnsemblRelease(75)
ensembl_grch38 = EnsemblRelease(79)

def expect_effect(
        variant,
        transcript_id,
        effect_class):
    transcript = variant.ensembl.transcript_by_id(transcript_id)
    effect = variant.effect_on_transcript(transcript)
    assert isinstance(effect, effect_class), \
        "Expected %s on %s to be %s, got %s" % (
            variant, transcript, effect_class.__name__, effect)


def test_incomplete():
    # transcript EGFR-009 (ENST00000450046 in Ensembl 78)
    # has an incomplete 3' end
    # chrom. 7 starting at 55,109,723
    # first exon begins: ATCATTCCTTTGGGCCTAGGA

    # change the first nucleotide of the 5' UTR A>T
    variant = Variant("7", 55109723, "A", "T", ensembl=ensembl_grch38)
    expect_effect(
        variant,
        transcript_id="ENST00000450046",
        effect_class=IncompleteTranscript)


def test_start_loss():
    # transcript EGFR-005 (ENST00000420316 in Ensembl 77)
    # location: chrom 7 @ 55,019,034-55,156,951 forward strand

    # CDS starts at position 244 of the first exon,
    # which is 55,019,034 + 244 of chr7 = 55019278
    # change the first two nucleotides of the 5' UTR AT>GG
    # making what used to be a start codon into GGG (Glycine)
    variant = Variant("7", 55019278, "AT", "GG", ensembl=ensembl_grch38)
    expect_effect(
        variant,
        transcript_id="ENST00000420316",
        effect_class=StartLoss)

def test_alternate_start_codon():
    # transcript EGFR-005 (ENST00000420316 in Ensembl 77)
    # location: chrom 7 @ 55,019,034-55,156,951 forward strand

    # CDS starts at position 244 of the first exon,
    # which is 55,019,034 + 244 of chr7 = 55019278
    # change the first nucleotide of the 5' UTR A>T
    # making what used to be the standard start codon ATG into TTG,
    # which normally codes for Leucine but can be used as an alternate
    # start codon
    variant = Variant("7", 55019278, "A", "T", ensembl=ensembl_grch38)
    expect_effect(
        variant,
        transcript_id="ENST00000420316",
        effect_class=AlternateStartCodon)


def test_stop_loss():
    # transcript MAST2-001 (ENST00000361297 in Ensembl 75)
    # location: chrom 1 @ 46,501,738 forward strand

    # change G>C in stop codon, should result in stop-loss mutation
    # causing an elongated protein
    variant = Variant("1", 46501738, "G", "C", ensembl=ensembl_grch37)
    expect_effect(
        variant,
        transcript_id="ENST00000361297",
        effect_class=StopLoss)

def test_stop_gain():
    # transcript BBRCA1-001 ENST00000357654 (looked up Ensembl 79)
    # Chromosome 17: 43,044,295-43,125,370 reverse strand.
    #
    # Let's look at exon #12
    # ENSE00003527960 43,082,575  43,082,404  start_phase = 0
    #
    # We can insert a reverse complement stop codon near the beginning since
    # the phase is 0.
    variant = Variant(
        "17",
        43082575 - 6,
        ref="",
        alt="CTA",
        ensembl=ensembl_grch38)
    expect_effect(
        variant,
        transcript_id="ENST00000357654",
        effect_class=PrematureStop)

def test_stop_gain_with_extra_amino_acids():
    # transcript BBRCA1-001 ENST00000357654 (looked up Ensembl 79)
    # Chromosome 17: 43,044,295-43,125,370 reverse strand.
    #
    # Let's look at exon #12
    # ENSE00003527960 43,082,575  43,082,404  start_phase = 0
    #
    # We can insert a reverse complement AAA followed by a stop codon
    # at near beginning since the phase is 0.
    variant = Variant(
        "17",
        43082575 - 6,
        ref="",
        alt="CTAAAA",
        ensembl=ensembl_grch38)
    expect_effect(
        variant,
        transcript_id="ENST00000357654",
        effect_class=PrematureStop)

def test_exon_loss():
    # transcript BBRCA1-001 ENST00000357654 (looked up Ensembl 79)
    # Chromosome 17: 43,044,295-43,125,370 reverse strand.
    #
    # Deleting exon #12
    # ENSE00003527960 43,082,575  43,082,404  start_phase = 0
    #
    variant = Variant(
        "17",
        43082404,
        ref="".join([
          "CTTTTTCTGATGTGCTTTGTTCTGGATTTCGCAGGTCCTCAAGGGCAGAAGAGTCACTTATGATG",
          "GAAGGGTAGCTGTTAGAAGGCTGGCTCCCATGCTGTTCTAACACAGCTTCAGTAATTAGATTAGT",
          "TAAAGTGATGTGGTGTTTTCTGGCAAACTTGTACACGAGCAT"
        ]),
        alt="",
        ensembl=ensembl_grch38)
    expect_effect(
        variant,
        transcript_id="ENST00000357654",
        effect_class=ExonLoss)


def test_exonic_splice_site():
    # transcript BBRCA1-001 ENST00000357654 (looked up Ensembl 79)
    # Chromosome 17: 43,044,295-43,125,370 reverse strand.
    #
    # Deleting last nucleotide of exon #12
    # ENSE00003527960 43,082,575  43,082,404  start_phase = 0
    #
    variant = Variant(
        "17",
        43082404,
        ref="C",
        alt="",
        ensembl=ensembl_grch38)
    expect_effect(
        variant,
        transcript_id="ENST00000357654",
        effect_class=ExonicSpliceSite)

def test_deletion():
    # transcript BBRCA1-001 ENST00000357654 (looked up Ensembl 79)
    # Chromosome 17: 43,044,295-43,125,370 reverse strand.
    #
    # Deleting second to last codon of exon #12
    # ENSE00003527960 43,082,575  43,082,404  start_phase = 0
    #
    variant = Variant(
        "17",
        43082404 + 4,
        ref="TTC",
        alt="",
        ensembl=ensembl_grch38)
    expect_effect(
        variant,
        transcript_id="ENST00000357654",
        effect_class=Deletion)

def test_insertion():
    # transcript BBRCA1-001 ENST00000357654 (looked up Ensembl 79)
    # Chromosome 17: 43,044,295-43,125,370 reverse strand.
    #
    # Insert codon after first two codons of exon #12
    # ENSE00003527960 43,082,575  43,082,404  start_phase = 0
    #
    variant = Variant(
        "17",
        43082575 - 6,
        ref="",
        alt="AAA",
        ensembl=ensembl_grch38)
    expect_effect(
        variant,
        transcript_id="ENST00000357654",
        effect_class=Insertion)

def test_frameshift():
    # transcript BBRCA1-001 ENST00000357654 (looked up Ensembl 79)
    # Chromosome 17: 43,044,295-43,125,370 reverse strand.
    #
    # Out of frame insertion after first two codons of exon #12
    # ENSE00003527960 43,082,575  43,082,404  start_phase = 0
    #
    variant = Variant(
        "17",
        43082575 - 6,
        ref="",
        alt="A",
        ensembl=ensembl_grch38)
    expect_effect(
        variant,
        transcript_id="ENST00000357654",
        effect_class=FrameShift)

def test_substitution():
    # transcript BBRCA1-001 ENST00000357654 (looked up Ensembl 79)
    # Chromosome 17: 43,044,295-43,125,370 reverse strand.
    #
    # Substitute second codon of exon #12 AGG > CCC (amino acid R>P)
    # ENSE00003527960 43,082,575  43,082,404  start_phase = 0
    #
    variant = Variant(
        "17",
        43082575 - 5,
        ref="CCT",
        alt="GGG",
        ensembl=ensembl_grch38)
    expect_effect(
        variant,
        transcript_id="ENST00000357654",
        effect_class=Substitution)

def test_silent():
    # transcript BBRCA1-001 ENST00000357654 (looked up Ensembl 79)
    # Chromosome 17: 43,044,295-43,125,370 reverse strand.
    #
    # Substitute second codon of exon #12 AGG > AGA (amino acid R>R silent)
    # ENSE00003527960 43,082,575  43,082,404  start_phase = 0
    #
    variant = Variant(
        "17",
        43082575 - 5,
        ref="CCT",
        alt="TCT",
        ensembl=ensembl_grch38)
    expect_effect(
        variant,
        transcript_id="ENST00000357654",
        effect_class=Silent)

def test_five_prime_utr():
    # transcript BBRCA1-001 ENST00000357654 (looked up Ensembl 79)
    # Chromosome 17: 43,044,295-43,125,370 reverse strand.
    #
    # Exon #1 is the beginning of the 5' UTR
    # 1 ENSE00001871077 43,125,370  43,125,271  -   -   length=100
    # Sequence:
    # GAGCTCGCTGAGACTTCCTGGACGGGGGACAGGCTGTGGGGTTTCTCAGATAACTGGGCC
    # CCTGCGCTCAGGAGGCCTTCACCCTCTGCTCTGGGTAAAG
    variant = Variant(
        "17",
        43125370 - 2,
        ref="CTC",
        alt="",
        ensembl=ensembl_grch38)
    expect_effect(
        variant,
        transcript_id="ENST00000357654",
        effect_class=FivePrimeUTR)

def test_three_prime_utr():
    # transcript BBRCA1-001 ENST00000357654 (looked up Ensembl 79)
    # Chromosome 17: 43,044,295-43,125,370 reverse strand.
    #
    # Exon #23 contains the 3' UTR
    # 23  ENSE00001814242 43,045,802  43,044,295  1   -   length=1,508
    # Sequence end with:
    # ...CACTTCCA
    variant = Variant(
        "17",
        43044295,
        ref="TGG",
        alt="",
        ensembl=ensembl_grch38)
    expect_effect(
        variant,
        transcript_id="ENST00000357654",
        effect_class=ThreePrimeUTR)

def test_intronic():
    # transcript BBRCA1-001 ENST00000357654 (looked up Ensembl 79)
    # Chromosome 17: 43,044,295-43,125,370 reverse strand.
    #
    # Insertion 20bp before exon #12 should be consider "Intronic"
    # #12 ENSE00003527960 43,082,575  43,082,404  start_phase = 0
    variant = Variant(
        "17",
        43082575 + 20,
        ref="",
        alt="CCC",
        ensembl=ensembl_grch38)
    expect_effect(
        variant,
        transcript_id="ENST00000357654",
        effect_class=Intronic)
