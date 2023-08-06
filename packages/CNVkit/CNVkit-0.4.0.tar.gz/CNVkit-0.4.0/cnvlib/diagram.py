"""Chromosome diagram drawing functions.

This uses and abuses Biopython's BasicChromosome module. It depends on
ReportLab, too, so we isolate this functionality here so that the rest of CNVkit
will run without it. (And also to keep the codebase tidy.)
"""
from __future__ import division
import collections
import math
import warnings

from Bio.Graphics import BasicChromosome as BC
from reportlab.graphics import renderPDF
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from . import core, plots

# Silence Biopython's whinging
from Bio import BiopythonWarning
warnings.simplefilter('ignore', BiopythonWarning)

TELOMERE_LENGTH = 6e6   # For illustration only
CHROM_FATNESS = 0.3
PAGE_SIZE = (11.0*inch, 8.5*inch)


def create_diagram(probe_pset, seg_pset, threshold, outfname, male_reference):
    """Create the diagram."""
    if probe_pset and seg_pset:
        is_seg = False
        do_both = True
    else:
        probe_pset = probe_pset or seg_pset
        if not probe_pset:
            raise ValueError("Must specify a filename as an argument or with "
                             "the '-s' option, or both. You did neither.")
        is_seg = bool(seg_pset)
        do_both = False

    # Consolidate genes & coverage values as chromsomal features
    features = collections.defaultdict(list)
    no_name = ('Background', 'CGH', '-', '.')
    strand = 1 if do_both else None
    probe_rows = core.shift_xx(probe_pset, male_reference)
    if not is_seg:
        probe_rows = probe_rows.squash_genes()
    for row in probe_rows:
        p_chrom, p_start, p_end, p_gene, p_coverage = tuple(row)[:5]
        if ((not is_seg) and (p_gene not in no_name)
            and abs(p_coverage) >= threshold):
            feat_name = p_gene
        else:
            feat_name = None
        features[p_chrom].append(
            (p_start - 1, p_end, strand, feat_name,
             colors.Color(*plots.cvg2rgb(p_coverage, not is_seg))))
    if do_both:
        for chrom, segrows in core.shift_xx(seg_pset, male_reference).by_chromosome():
            features[chrom].extend(
                (srow['start'] - 1, srow['end'], -1, None,
                 colors.Color(*plots.cvg2rgb(srow['coverage'], False)))
                for srow in segrows)

    # Generate the diagram PDF
    if not outfname:
        outfname = probe_pset.sample_id + '-diagram.pdf'
    chrom_sizes = plots.chromosome_sizes(probe_pset)
    drawing = build_chrom_diagram(features, chrom_sizes, probe_pset.sample_id)
    cvs = canvas.Canvas(outfname, pagesize=PAGE_SIZE)
    renderPDF.draw(drawing, cvs, 0, 0)
    cvs.showPage()
    cvs.save()
    return outfname


def build_chrom_diagram(features, chr_sizes, sample_id):
    """Create a PDF of color-coded features on chromosomes."""
    max_chr_len = max(chr_sizes.values())

    chr_diagram = BC.Organism()
    chr_diagram.page_size = PAGE_SIZE
    chr_diagram.title_size = 18

    for chrom, length in chr_sizes.items():
        chrom_features = features.get(chrom)
        if not chrom_features:
            continue
        body = BC.AnnotatedChromosomeSegment(length, chrom_features)
        body.label_size = 4
        body.scale = length
        body.chr_percent = CHROM_FATNESS

        # Create opening and closing telomeres
        tel_start = BC.TelomereSegment()
        tel_start.scale = TELOMERE_LENGTH
        tel_start.chr_percent = CHROM_FATNESS
        tel_end = BC.TelomereSegment(inverted=True)
        tel_end.scale = TELOMERE_LENGTH
        tel_end.chr_percent = CHROM_FATNESS

        # Assemble the chromosome diagram in order
        cur_chromosome = BC.Chromosome(chrom)
        cur_chromosome.title_size = 14
        # Set the scale to the MAXIMUM length plus the two telomeres in bp,
        # want the same scale used on all chromosomes so they can be
        # compared to each other
        cur_chromosome.scale_num = max_chr_len + 2 * TELOMERE_LENGTH
        cur_chromosome.add(tel_start)
        cur_chromosome.add(body)
        cur_chromosome.add(tel_end)
        chr_diagram.add(cur_chromosome)

    title = "Sample " + sample_id
    return bc_organism_draw(chr_diagram, title)


def bc_organism_draw(org, title, wrap=12):
    """Modified copy of Bio.Graphics.BasicChromosome.Organism.draw.

    Instead of stacking chromosomes horizontally (along the x-axis), stack rows
    vertically, then proceed with the chromosomes within each row.

    Arguments:

    - title: The output title of the produced document.
    """
    margin_top = 1.25*inch
    margin_bottom = 0.1*inch
    margin_side = 0.5*inch

    width, height = org.page_size
    cur_drawing = BC.Drawing(width, height)

    # Draw the title text
    title_string = BC.String(width / 2, height - margin_top + .5*inch, title)
    title_string.fontName = 'Helvetica-Bold'
    title_string.fontSize = org.title_size
    title_string.textAnchor = "middle"
    cur_drawing.add(title_string)

    # Layout subcomponents (individual chromosomes), wrapping into rows
    if len(org._sub_components) > 0:
        nrows = math.ceil(len(org._sub_components) / wrap)
        x_pos_change = (width - 2 * margin_side) / wrap
        y_pos_change = (height - margin_top - margin_bottom) / nrows

    cur_x_pos = margin_side
    cur_row = 0
    for i, sub_component in enumerate(org._sub_components):
        if i % wrap == 0 and i != 0:
            cur_row += 1
            cur_x_pos = margin_side
        # Set the page coordinates of the chromosome drawing
        sub_component.start_x_position = cur_x_pos + 0.05 * x_pos_change
        sub_component.end_x_position = cur_x_pos + 0.95 * x_pos_change
        sub_component.start_y_position = (height - margin_top
                                          - y_pos_change * cur_row)
        sub_component.end_y_position = (margin_bottom
                                        + y_pos_change * (nrows - cur_row - 1))
        # Render the chromosome drawing
        sub_component.draw(cur_drawing)
        # Update the locations for the next chromosome
        cur_x_pos += x_pos_change

    # Draw a legend
    # (Rect coordinates are: left, bottom, width, height)
    # Bounding box -- near-bottom, center
    cur_drawing.add(BC.Rect(width/2 - .8*inch, .5*inch, 1.6*inch, .4*inch,
                            fillColor=colors.white))
    # Red box & label -- in left half of bounding box
    cur_drawing.add(BC.Rect(width/2 - .7*inch, .6*inch, .2*inch, .2*inch,
                            fillColor=colors.Color(.8, .2, .2)))
    cur_drawing.add(BC.String(width/2 - .42*inch, .65*inch, "Gain",
                              fontName='Helvetica', fontSize=12))
    # Blue box & label -- in right half of bounding box
    cur_drawing.add(BC.Rect(width/2 + .07*inch, .6*inch, .2*inch, .2*inch,
                            fillColor=colors.Color(.2, .2, .8)))
    cur_drawing.add(BC.String(width/2 + .35*inch, .65*inch, "Loss",
                              fontName='Helvetica', fontSize=12))

    # Let the caller take care of writing to the file...
    return cur_drawing


def bc_chromosome_draw_label(self, cur_drawing, label_name):
    """Monkeypatch to Bio.Graphics.BasicChromosome.Chromosome._draw_label.

    Draw a label for the chromosome. Mod: above the chromosome, not below.
    """
    # Center on chromosome image
    x_position = 0.5 * (self.start_x_position + self.end_x_position)
    # Place at the bottom of the diagram?
    y_position = self.start_y_position + 0.1*inch  # was: self.end_y_position
    label_string = BC.String(x_position, y_position, label_name)
    label_string.fontName = 'Times-BoldItalic'
    label_string.fontSize = self.title_size
    label_string.textAnchor = 'middle'
    cur_drawing.add(label_string)

BC.Chromosome._draw_label = bc_chromosome_draw_label
