// Some data for the demo.

// We are going to use the same data source for multiple tracks
var bamSource = pileup.formats.bam({
  url: '/test-data/aln.sorted.bam',
  indexUrl: '/test-data/aln.sorted.bam.bai'
});

var sources = [
  {
    viz: pileup.viz.signalplot(),
    data: bamSource,
    name: "Signal Plot"
  },
  {
    viz: pileup.viz.scale(),
    name: 'Scale'
  },
  {
    viz: pileup.viz.genome(),
    isReference: true,
    data: pileup.formats.twoBit({
      url: '/test-data/lambda_ref.2bit'
    }),
    name: 'Reference'
  },
  {
    viz: pileup.viz.location(),
    name: 'Location'
  },
  {
    viz: pileup.viz.coverage(),
    data: bamSource,
    cssClass: 'normal',
    name: 'Coverage'
  },
  {
    viz: pileup.viz.pileup(),
    data: bamSource,
    cssClass: 'normal',
    name: 'Alignments'
  }
];
var range = {contig: 'burn-in', start: 1, stop: 157};
