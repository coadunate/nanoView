/**
 * Signal Plot visualization for the alignments.
 * @flow
 */
'use strict';

import type {VizProps} from '../VisualizationWrapper';
import type {DataCanvasRenderingContext2D} from 'data-canvas';
import type {Scale} from './d3utils';

import React from 'react';
import ReactDOM from 'react-dom';
import shallowEquals from 'shallow-equals';

import scale from '../scale';
import canvasUtils from './canvas-utils';
import ContigInterval from '../ContigInterval';
import dataCanvas from 'data-canvas';
import d3utils from './d3utils';
import TiledCanvas from './TiledCanvas';
import _ from 'underscore';
import style from '../style';



function renderSignalPlot(ctx: DataCanvasRenderingContext2D,
                      scale: (num: number) => number,
                      height: number,
                      range: ContigInterval<string>,
                      events_all: any,
                      yScale: (num: number) => number,
                      hideNonBaseCalled: boolean,
                      lWidth: number,
                      arcRadius: number) {

  var start = range.start(),
      stop = range.stop();

  var read_num = 0; // count the read number for READ_COLOR array.
  // Loop through everything in the events_all array except the last, which is the min and max
  // signal values.
  for(var i = 0;  i < events_all.length-1; i++){
    if(i%2!=0){ // The odd entries represent the array of events.
      read_num++;
      var sub_events = [];
      for(var j = 0; j < events_all[i].length; j++){ // each event is array of sub events
        if(j%2!=0){ // the odd ones are event records and even are the event number.
          sub_events.push(events_all[i][j]);
        }
      }

      // PLOT SIGNAL PATH

      ctx.beginPath();
      ctx.moveTo(scale(start + 0.5), yScale(sub_events[start-start][0][1]));
      // Plot the non-basecalled path.
      for(var n = 1; n < sub_events[start-start].length; n++){
        ctx.lineTo(scale(start + 0.5 + (sub_events[start-start][n][0] - sub_events[start-start][0][0]) ), yScale(sub_events[start-start][n][1]));
      }
      // Plot the base-called path.
      for(var pos = start+1; pos <= stop; pos++){
        ctx.save();
        ctx.pushObject({pos});

        ctx.lineTo(scale(pos+0.5), yScale(sub_events[pos-start][0][1]));

        // Plot the non-basecalled path.
        for(var p = 1; p < sub_events[pos-start].length; p++){
          ctx.lineTo(scale(pos + 0.5 +  (sub_events[pos-start][p][0] - sub_events[pos-start][0][0]) ), yScale(sub_events[pos-start][p][1]));
        }
        ctx.strokeStyle=style.READ_COLORS[read_num-1];
        ctx.lineWidth=lWidth;
        ctx.stroke();

        ctx.popObject();
        ctx.restore();

      }
      ctx.closePath();

      // PLOT SIGNAL EVENT POINTS.

      // plot the first point.
      ctx.fillStyle="red";
      ctx.beginPath();
      ctx.arc(scale(start + 0.5), yScale(sub_events[start-start][0][1]), arcRadius, 0,2*Math.PI);
      ctx.closePath();
      ctx.fill();


      if(!hideNonBaseCalled){

        // plot the starting non-basecalled points if you're supposed to.
        for(var q = 1; q < sub_events[start-start].length; q++){
          ctx.fillStyle="gray";
          ctx.beginPath();
          ctx.arc(scale(start + 0.5 + (sub_events[start-start][q][0] - sub_events[start-start][0][0]) ), yScale(sub_events[start-start][q][1]), arcRadius, 0,2*Math.PI);
          ctx.closePath();
          ctx.fill();
        }
      }

      for(var pos1 = start+1; pos1 <= stop; pos1++){

        ctx.save();
        ctx.pushObject({pos1});

        // plot the base-called points.
        ctx.fillStyle = "red";
        ctx.beginPath();
        ctx.arc(scale(pos1 + 0.5), yScale(sub_events[pos1-start][0][1]), arcRadius, 0,2*Math.PI);
        ctx.closePath();
        ctx.fill();

        if(!hideNonBaseCalled){
          // plot the ret of non-basecalled points if you're suppos1ed to
          for(var n1 = 1; n1 < sub_events[pos1-start].length; n1++){
            ctx.fillStyle = "gray";
            ctx.beginPath();
            ctx.arc(scale(pos1 + 0.5 + (sub_events[pos1-start][n1][0] - sub_events[pos1-start][0][0]) ), yScale(sub_events[pos1-start][n1][1]), arcRadius, 0,2*Math.PI);
            ctx.closePath();
            ctx.fill();
          }
        }

        ctx.popObject();
        ctx.restore();
      }

    }

  }

}


class SignalPlotCanvas extends TiledCanvas {
  height: number;

  /** Returns a JSON array containing the event information of the given range. */
  getEventData(range: GenomeRange) {
    var result = [];
    var xhttp = new XMLHttpRequest();

    xhttp.open("GET", "http://127.0.0.1:5000/getrange/start=" + range.start + "&end=" + (range.stop+1) + "&name=semifinaldataset", false);
    xhttp.onload = function() {
      result = JSON.parse(xhttp.responseText);

    };
    xhttp.send();
    return result;
    // event.preventDefault();
  }

  update(newOptions: Object) {
    this.options = newOptions;
  }

  yScaleForRef(maxSignal: number, bottomPadding: number, topPadding:number): (y: number) => number {
    return scale.linear()
      .domain([maxSignal, 0])
      .range([bottomPadding, this.height - topPadding - 100])
      .nice();
  }

  constructor(height: number, options: Object) {
    super();
    // workaround for an issue in PhantomJS where height always comes out to zero.
    this.height = Math.max(1, height);
    this.options = options;

  }

  render(ctx: DataCanvasRenderingContext2D,
         scale: (x: number)=>number,
         range: ContigInterval<string>) {
    // The +/-1 ensures that partially-visible bases on the edge are rendered.
    var genomeRange = {
      contig: range.contig,
      start: Math.max(0, range.start() - 1),
      stop: range.stop() + 1
    };
    var evnts = this.getEventData(genomeRange);

    var maxSignal = 200;
    var yScale = this.yScaleForRef(maxSignal,0,0);
    var lineWidth;
    if(this.options.SignalLineQuarter) lineWidth = 0.25;
    else if(this.options.SignalLineHalf) lineWidth = 0.5;
    else if(this.options.SignalLineNormal) lineWidth = 1;
    else if(this.options.SignalLineDouble) lineWidth = 2;
    else if(this.options.SignalLineQuad) lineWidth = 4;
    else lineWidth = 1;

    var arcRadius;
    if(this.options.SignalArcHalf) arcRadius = 0.5;
    else if(this.options.SignalArcNormal) arcRadius = 1;
    else if(this.options.SignalArcDouble) arcRadius = 2;
    else if(this.options.SignalArcQuad) arcRadius = 4;
    else arcRadius = 1;

    if(evnts.length > 0) {
      renderSignalPlot(ctx, scale, this.height, ContigInterval.fromGenomeRange(genomeRange), evnts, yScale, this.options.hideNonBaseCalled, lineWidth, arcRadius);
    }
  }

  heightForRef(ref: string): number {
    return this.height;
  }

  updateHeight(height: number) {
    this.height = height;
  }
}


class SignalPlot extends React.Component {
  props: VizProps;
  state: void;  // no state
  tiles: SignalPlotCanvas;
  static defaultOptions: { hideNonBaseCalled: boolean };
  static getOptionsMenu: (options: Object) => any;
  static handleSelectOption: (key: string, oldOptions: Object) => Object;
  render(): any {
    return <canvas />;
  }

  componentDidMount() {
    this.tiles = new SignalPlotCanvas(this.props.height, this.props.options);
    this.updateVisualization();
  }

  getScale(): Scale {
    return d3utils.getTrackScale(this.props.range, this.props.width);
  }

  componentDidUpdate(prevProps: any, prevState: any) {
    var shouldUpdate = false;

    if (this.props.options != prevProps.options){
      this.handleOptionsChange(prevProps.options);
      shouldUpdate = true;
    }

    if (!shallowEquals(prevProps, this.props) ||
        !shallowEquals(prevState, this.state)) {
      if (this.props.height != prevProps.height) {
        this.tiles.updateHeight(this.props.height);
        this.tiles.invalidateAll();
      }
      this.updateVisualization();
    }
  }

  handleOptionsChange(oldOpts: Object) {
    this.tiles.invalidateAll();

    if (oldOpts.hideNonBaseCalled != this.props.options.hideNonBaseCalled) {
      this.tiles = new SignalPlotCanvas(this.props.height, this.props.options);
      this.tiles.invalidateAll();
      this.updateVisualization();
    } else if(oldOpts.SignalLineQuarter != this.props.options.SignalLineQuarter){
      this.tiles = new SignalPlotCanvas(this.props.height, this.props.options);
      this.tiles.invalidateAll();
      this.updateVisualization();
    } else if(oldOpts.SignalLineHalf != this.props.options.SignalLineHalf){
      this.tiles = new SignalPlotCanvas(this.props.height, this.props.options);
      this.tiles.invalidateAll();
      this.updateVisualization();
    } else if(oldOpts.SignalLineNormal != this.props.options.SignalLineNormal){
      this.tiles = new SignalPlotCanvas(this.props.height, this.props.options);
      this.tiles.invalidateAll();
      this.updateVisualization();
    }else if(oldOpts.SignalLineDouble != this.props.options.SignalLineDouble){
      this.tiles = new SignalPlotCanvas(this.props.height, this.props.options);
      this.tiles.invalidateAll();
      this.updateVisualization();
    } else if(oldOpts.SignalLineQuad != this.props.options.SignalLineQuad){
      this.tiles = new SignalPlotCanvas(this.props.height, this.props.options);
      this.tiles.invalidateAll();
      this.updateVisualization();

    } else if(oldOpts.SignalArcHalf != this.props.options.SignalArcHalf){
      this.tiles = new SignalPlotCanvas(this.props.height, this.props.options);
      this.tiles.invalidateAll();
      this.updateVisualization();
    } else if(oldOpts.SignalArcNormal != this.props.options.SignalArcNormal){
      this.tiles = new SignalPlotCanvas(this.props.height, this.props.options);
      this.tiles.invalidateAll();
      this.updateVisualization();
    } else if(oldOpts.SignalArcDouble != this.props.options.SignalArcDouble){
      this.tiles = new SignalPlotCanvas(this.props.height, this.props.options);
      this.tiles.invalidateAll();
      this.updateVisualization();
    } else if(oldOpts.SignalArcQuad != this.props.options.SignalArcQuad){
      this.tiles = new SignalPlotCanvas(this.props.height, this.props.options);
      this.tiles.invalidateAll();
      this.updateVisualization();
    }
  }

  updateVisualization() {
    var canvas = ReactDOM.findDOMNode(this),
        {width, height, range} = this.props;

    // Hold off until height & width are known.
    if (width === 0) return;
    d3utils.sizeCanvas(canvas, width, height);

    var ctx = dataCanvas.getDataContext(canvasUtils.getContext(canvas));
    ctx.reset();
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    this.tiles.renderToScreen(ctx, ContigInterval.fromGenomeRange(range), this.getScale());
  }
}

SignalPlot.displayName = 'signalplot';

SignalPlot.displayName = 'signalplot';
SignalPlot.defaultOptions = {

  hideNonBaseCalled: false,
  SignalLineQuarter: false,
  SignalLineHalf: false,
  SignalLineNormal: true,
  SignalLineDouble: false,
  SignalLineQuad: false,

  SignalArcHalf: false,
  SignalArcNormal: false,
  SignalArcDouble: true,
  SignalArcQuad: false
};

SignalPlot.getOptionsMenu = function(options: Object): any {
  return [
    {key: 'hide-non-basecalled', label: 'Hide Non Basecalled Events', checked: options.hideNonBaseCalled},
    '-',
    {key: 'sline-quarter', label: 'Signal Line Quarter (1/4px)', checked: options.SignalLineQuarter},
    {key: 'sline-half', label: 'Signal Line Half (1/2px)', checked: options.SignalLineHalf},
    {key: 'sline-normal', label: 'Signal Line Normal (1px)', checked: options.SignalLineNormal},
    {key: 'sline-double', label: 'Signal Line Double (2px)', checked: options.SignalLineDouble},
    {key: 'sline-quad', label: 'Signal Line Quad (4px)', checked: options.SignalLineQuad},
    '-',
    {key: 'sarc-half', label: 'Signal Arc Half (1/2)', checked: options.SignalArcHalf},
    {key: 'sarc-normal', label: 'Signal Arc Normal (1)', checked: options.SignalArcNormal},
    {key: 'sarc-double', label: 'Signal Arc Double (2)', checked: options.SignalArcDouble},
    {key: 'sarc-quad', label: 'Signal Arc Quad (4)', checked: options.SignalArcQuad}
  ];
};


SignalPlot.handleSelectOption = function(key: string, oldOptions: Object): Object {
  var opts = _.clone(oldOptions);
  if (key == 'hide-non-basecalled') {
    opts.hideNonBaseCalled = !opts.hideNonBaseCalled;
    return opts;
  } else if(key == 'sline-quarter'){
    opts.SignalLineQuarter = !opts.SignalLineQuarter;
    if (opts.SignalLineQuarter) {
      opts.SignalLineHalf = false;
      opts.SignalLineNormal = false;
      opts.SignalLineDouble = false;
      opts.SignalLineQuad = false;
    }
    return opts;
  } else if(key == 'sline-half'){
    opts.SignalLineHalf = !opts.SignalLineHalf;
    if(opts.SignalLineHalf) {
      opts.SignalLineQuarter = false;
      opts.SignalLineNormal = false;
      opts.SignalLineDouble = false;
      opts.SignalLineQuad = false;
    }
    return opts;
  } else if(key == 'sline-normal'){
    opts.SignalLineNormal = !opts.SignalLineNormal;
    if(opts.SignalLineNormal){
      opts.SignalLineQuarter = false;
      opts.SignalLineHalf = false;
      opts.SignalLineDouble = false;
      opts.SignalLineQuad = false;
    }
    return opts;
  } else if(key == 'sline-double'){
    opts.SignalLineDouble = !opts.SignalLineDouble;
    if(opts.SignalLineDouble){
      opts.SignalLineQuarter = false;
      opts.SignalLineHalf = false;
      opts.SignalLineNormal = false;
      opts.SignalLineQuad = false;
    }
    return opts;
  } else if(key == 'sline-quad'){
    opts.SignalLineQuad = !opts.SignalLineQuad;
    if(opts.SignalLineQuad){
      opts.SignalLineQuarter = false;
      opts.SignalLineHalf = false;
      opts.SignalLineNormal = false;
      opts.SignalLineDouble = false;
    }
    return opts;

  } else if(key == 'sarc-half'){
    opts.SignalArcHalf = !opts.SignalArcHalf;
    if(opts.SignalArcHalf){
      opts.SignalArcNormal = false;
      opts.SignalArcDouble = false;
      opts.SignalArcQuad = false;
    }
    return opts;
  } else if(key == 'sarc-normal'){
    opts.SignalArcNormal = !opts.SignalArcNormal;
    if(opts.SignalArcNormal){
      opts.SignalArcHalf = false;
      opts.SignalArcDouble = false;
      opts.SiganlArcQuad = false;
    }
    return opts;
  } else if(key == 'sarc-double'){
    opts.SignalArcDouble = !opts.SignalArcDouble;
    if(opts.SignalArcDouble){
      opts.SignalArcHalf = false;
      opts.SignalArcNormal = false;
      opts.SignalArcQuad = false;
    }
    return opts;
  } else if(key == 'sarc-quad'){
    opts.SignalArcQuad = !opts.SignalArcQuad;
    if(opts.SignalAarcQuad){
      opts.SignalArcHalf = false;
      opts.SignalArcNormal = false;
      opts.SignalArcDouble = false;
    }
    return opts;
  }
  return oldOptions;  // no change
};


module.exports = SignalPlot;
