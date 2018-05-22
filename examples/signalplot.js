// SignalPlot.json
// The main functionality of the application

// Initial Settings of the Line Plot.

addons = {
  line: 0,
  non_basecalled: true,
  width: 2
}


reA2012 = new RegExp('.*A2012.*');
reAmes = new RegExp('.*Ames.*');

var READ_COLORS = [
  "#F5A9A9",
  "#F3E2A9",
  "#BEF781",
  "#81F79F",
  "#81F7D8",
  "#58ACFA",
  "#8258FA",
  "#9A2EFE",
  "#FE2EF7"
];

var BASECOLORS = {
  'A': 'green',
  'G': 'orange',
  'C': 'blue',
  'T': 'red'
};

var drawingOptions = {
  lineColor: 'blue'
}


// This next chunk of code draws the control buttons to the screen

var mainButtonsDiv = document.getElementById("mainButtons");

var imageInput = document.createElement("INPUT");
imageInput.setAttribute("type","text");
imageInput.setAttribute("placeholder","image URL");
mainButtonsDiv.appendChild(imageInput);

mainButtonsDiv.appendChild(document.createElement('span').appendChild(document.createTextNode(' ')))

var infoImage = document.getElementById("infoImage");

var imgButton = document.createElement("BUTTON");
imgButton.appendChild(document.createTextNode("LOAD IMAGE"));
mainButtonsDiv.appendChild(imgButton);
imgButton.addEventListener('click',function(){
  document.getElementsByClassName("signalplot")[0].style.minHeight= "1030px";
  infoImage.src = imageInput.value;
});

mainButtonsDiv.appendChild(document.createElement('span').appendChild(document.createTextNode(' ')))

var unloadImage = document.createElement("BUTTON");
unloadImage.appendChild(document.createTextNode("UNLOAD IMAGE"));
mainButtonsDiv.appendChild(unloadImage);
unloadImage.addEventListener('click',function(){
  document.getElementsByClassName("signalplot")[0].style.minHeight= "500px";
  infoImage.src="";

});

mainButtonsDiv.appendChild(document.createElement('span').appendChild(document.createTextNode(' ● ')))


var oneReadLambda = document.createElement("BUTTON");
oneReadLambda.appendChild(document.createTextNode("1 Read Lambda"));
mainButtons.appendChild(oneReadLambda);
oneReadLambda.addEventListener('click',function(){
  removeRendering();
  renderEventData('206.167.183.18','data-bp20',2,addons,[-2,82]);
  showButtons('any','data-bp20');
});

var sixReadLambda = document.createElement("BUTTON");
sixReadLambda.appendChild(document.createTextNode("6 Read Lambda"));
mainButtons.appendChild(sixReadLambda);
sixReadLambda.addEventListener('click', function(){
  removeRendering();
  renderEventData('206.167.183.18','tombo-may26',2,addons,[-2,82]);
  showButtons('any','tombo-may26');
});

var salmonellaSNP = document.createElement("BUTTON");
salmonellaSNP.appendChild(document.createTextNode("Salmonella SNP"));
mainButtons.appendChild(salmonellaSNP);
salmonellaSNP.addEventListener('click',function(){
  removeRendering();
  renderEventData('206.167.183.18','salmonella32',2,addons,null);
  showButtons('any','salmonella32');
});

var BAnthracis = document.createElement("BUTTON");
BAnthracis.appendChild(document.createTextNode("B. anthracis."));
mainButtons.appendChild(BAnthracis);
BAnthracis.addEventListener('click',function(){
  removeRendering();
  renderEventData('206.167.183.18','sim_dset',2,addons,null);
  showButtons('any','sim_dset');
});

var phytoplasmaSNP = document.createElement("BUTTON");
phytoplasmaSNP.appendChild(document.createTextNode("Phytoplasma SNP"));
mainButtons.appendChild(phytoplasmaSNP);
phytoplasmaSNP.addEventListener('click',function(){
  removeRendering();
  renderEventData('206.167.183.18','tombo-may26',2,addons,null);
  showButtons('any','tombo-may26');
});

var tomboPlusRawButton = document.createElement("BUTTON");
tomboPlusRawButton.appendChild(document.createTextNode("TOMBO + NORMALIZED SIGNAL"));
mainButtonsDiv.appendChild(tomboPlusRawButton);
tomboPlusRawButton.addEventListener('click',function(){
  removeRendering();
  addons.non_basecalled = true;
  renderEventData('206.167.183.18','tombo-may30',2,addons,[-2,82]);
  showButtons('any','tombo-may30');
});

var sixReadTombo = document.createElement("BUTTON");
sixReadTombo.appendChild(document.createTextNode("6 Read Lambda + TOMBO"));
mainButtonsDiv.appendChild(sixReadTombo);
sixReadTombo.addEventListener('click',function(){
  removeRendering();
  renderEventData('206.167.183.18','tombo-may31',2,addons,[-2,82]);
  showButtons('any','tombo-may31');
});

mainButtonsDiv.appendChild(document.createElement('span').appendChild(document.createTextNode(' → ')))

var additionalButtons = document.createElement("div");
additionalButtons.setAttribute("style","display:inline-block");
mainButtonsDiv.append(additionalButtons);

function showButtons(dataset='none',dataset_name){
  while(additionalButtons.firstChild){
    additionalButtons.removeChild(additionalButtons.firstChild);
  }
  if(dataset == 'any'){
    var text;

    var given_range = null;
    if(dataset_name == 'data-bp20' || dataset_name == 'tombo-may26' || dataset_name =='tombo-may30' || dataset_name == 'tombo-may31') given_rage = [-2,82]
    else if(dataset_name == 'salmonella32') given_range = [3910,3920];


    if(addons.line == 0) text="No line";
    else if(addons.line == 1) text="Euclidean"
    else if(addons.line == 2) text="Step line"
    var b5 = document.createElement("BUTTON");
    b5.appendChild(document.createTextNode("TOGGLE LINES: " + text));
    additionalButtons.append(b5);
    b5.addEventListener('click',function(){
      removeRendering();
      addons.line = (addons.line+1)%3;
      b5.innerText="TOGGLE LINES: " + text;
      renderEventData('206.167.183.18',dataset_name,2,addons,given_range);
      showButtons('any',dataset_name);
    });


    var b6 = document.createElement("BUTTON");
    b6.appendChild(document.createTextNode("Width: " + addons.width));
    additionalButtons.append(b6);
    b6.addEventListener('click',function(){
      removeRendering();
      addons.width = (addons.width+1)%3;
      renderEventData('206.167.183.18',dataset_name,2,addons,given_range);
      showButtons('any',dataset_name);

    });
  }
}

// define all size variables
var margin = {top: 60, right: 10, bottom: 30, left: 120};
var fullWidth = window.innerWidth - margin.right;
var fullHeight = 500;
var width = fullWidth - margin.left - margin.right;
var height = fullHeight - margin.top - margin.bottom;

// the canvas is shifted by 1px to prevent any artefacts
// when the svg axis and the canvas overlap
var canvas = d3.select("#plot-canvas")
    .attr("width", width - 1)
    .attr("height", height - 1)
    .style("transform", "translate(" + (margin.left + 1) +
        "px" + "," + (margin.top + 1) + "px" + ")");


var svg = d3.select("#axis-svg")
    .attr("width", fullWidth)
    .attr("height", fullHeight)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," +
        (margin.top) + ")");


// get the canvas drawing context
var context = canvas.node().getContext('2d');

function removeRendering(){
  context.clearRect(0, 0, fullWidth, fullHeight);
  svg.selectAll("*").remove();
}

function renderEventData(url,datasetname, dataType, addition = {line: 0},given_range){

  /** Returns a JSON array containing the event information */
  var getEventData = function() {
    var result = [];
    var xhttp = new XMLHttpRequest();

    xhttp.open("GET", "http://" + url + ":5000/getall/name=" + datasetname + "&data="  + dataType, false);
    xhttp.onload = function() {
      result = JSON.parse(xhttp.responseText);
    };
    xhttp.send();
    var eventData = [];
    var finalDataset = [];
    for(var i = 0; i < result.length; i++){
      if(i%2!=0){
        var x = []; // contains [x,cigarStatus, base]
        var y = [];
        var subEv = [];
        if(dataType == 1 || dataType == 2){ // tombo dataset is enclosed in an arry.
          for(var j = 0; j < result[i][0].length; j++){
              if(j%2!= 0){
                subEv.push(result[i][0][j]);
            }
          }
        } else if(dataType == 0){
          for(var j = 0; j < result[i].length; j++){
            if(j%2!= 0){
              subEv.push(result[i][j]);
            }
          }
        }
        for(var k = 0; k < subEv.length; k++){
          var dCounter = 0;
          for(var l = 0; l < subEv[k].length; l++){
            if(datasetname == 'sim_dset' && subEv[k][l][3] == "i") continue;
            else if(datasetname == 'sim_dset' && subEv[k][l][3] == "d") dCounter++;
            var _x = [];
            _x.push(Number(subEv[k][l][0]) + dCounter); // x value
            _x.push(subEv[k][l][3]); // cigar status
            _x.push(subEv[k][l][2]); // base
            x.push(_x);
            y.push(Number(subEv[k][l][1]));

          }
        }


        eventData.push(x);
        eventData.push(y);

      }
    }

    finalReads = [];
    for(var x =0; x < eventData.length; x += 2){
      var arr = [];
      arr.push(eventData[x]);
      arr.push(eventData[x+1]);
      arr.push(result[x]);
      finalReads.push(arr);
    }
    return finalReads;
  }

  var resultEvent = getEventData();
  var data = [];
  for(var x = 0; x < resultEvent.length; x++){
    var inter_data = [];
    for(var a = 0; a < resultEvent[x][0].length; a++){
      if(dataType == 2){

        if(datasetname == 'sim_dset'){
          // console.log("SIM DATASET")
          var datum = {
            x: resultEvent[x][0][a][0], // x value
            y: resultEvent[x][1][a],
            name: resultEvent[x][2],
            base: resultEvent[x][0][a][2], // basepair
            cigarStatus: resultEvent[x][0][a][1] // Cigar status

          }
        } else {
          // console.log("OTHER DATASET")

          var datum = {
            y: resultEvent[x][0][a][0], // x value
            x: resultEvent[x][1][a],
            name: resultEvent[x][2],
            base: resultEvent[x][0][a][2], // basepair
            cigarStatus: resultEvent[x][0][a][1] // Cigar status

          }
        }
      } else{
        var datum = {
          x: resultEvent[x][0][a][0], // x value
          y: resultEvent[x][1][a],
          name: resultEvent[x][2],
          cigarStatus: resultEvent[x][0][a][1] // Cigar status

        }
      }
      inter_data.push(datum);

    }
    data.push(inter_data);
  }


  var xRange = [Infinity,-Infinity];
  var yRange = [Infinity,-Infinity];

  data.forEach(function(d,i){
    var _xRange = d3.extent(d, function(e){ return e.x });

    if(_xRange[0] < xRange[0]) xRange[0] = _xRange[0];
    if(_xRange[1] > xRange[1]) xRange[1] = _xRange[1];

    var _yRange = d3.extent(d, function(e){ return e.y; });

    if(_yRange[0] < yRange[0]) yRange[0] = _yRange[0];
    if(_yRange[1] > yRange[1]) yRange[1] = _yRange[1];

  });
  // Creates the xScale for the plot.
  var xScale = d3.scale.linear()
      //.domain([4879834,4879893])   // @MATT: Lower and upper bound for the x-axis.
      .domain(given_range == null ? [xRange[0],xRange[1]] : given_range)
      //.domain([xRange[0],xRange[1]])
      .range([0, width]);


  // Creates the yScale for the plot.
  var yScale = d3.scale.linear()
      .domain([yRange[0],yRange[1]]) // @MATT: Lower and upper bound for the y-axis.
      .range([height, 0]);

  var xAxis = d3.svg.axis()
      .scale(xScale)
      .innerTickSize(-height)
      .outerTickSize(0)
      .tickPadding(10)
      .orient('bottom');

  var yAxis = d3.svg.axis()
      .scale(yScale)
      .innerTickSize(-width)
      .outerTickSize(0)
      .orient('left');

  // create zoom behaviour
  var zoomBehaviour = d3.behavior.zoom()
      .x(xScale)          // @MATT: Comment this line if you want the x-axis to be static.
      // .y(yScale)     // @MATT: Comment this line if you want the y-axis to be static.
      .scaleExtent([1, 1000])
      .on("zoom", onZoomEnd)
      //.on("zoomend", onZoomEnd);

  // zoomBehaviour.scale(57,5);

  // append x-axis, y-axis
  var xAxisSvg = svg.append('g')
      .attr('class', 'x axis')
      .attr('transform', 'translate(0,' + height + ')')
      .call(xAxis);

  var yAxisSvg = svg.append('g')
      .attr('class', 'y axis')
      .call(yAxis);

  // add zoom behaviour
  canvas.call(zoomBehaviour);


  draw(drawingOptions);


  function onZoom() {
      var _range = {contig: 'burn-in', start: Math.round(xScale.domain()[0]), stop: Math.round(xScale.domain()[1]) };
      p.setRange(_range);
  }

  function onZoomEnd(dOpts) {

      var midPoint = Math.round(xScale.domain()[0] + (xScale.domain()[1]-xScale.domain()[0])/2);
      if(dOpts)
        draw(dOpts,midPoint);
      else
        draw(drawingOptions,midPoint);
      xAxisSvg.call(xAxis);
      yAxisSvg.call(yAxis);


      var _range = {contig: 'burn-in', start: Math.round(xScale.domain()[0]), stop: Math.round(xScale.domain()[1]) };

      p.setRange(_range);

      // DRAWS THE LEFT MIDDLE LINE
      context.beginPath();
      context.setLineDash([15, 20]);
      context.moveTo(xScale(midPoint-1),yScale(-20));
      context.lineTo(xScale(midPoint-1),0);
      context.strokeStyle="black";
      context.lineWidth=1;
      context.closePath();
      context.stroke();

      // DRAWS THE RIGHT MIDDLE LINE
      context.beginPath();
      context.moveTo(xScale(midPoint),yScale(-20));
      context.lineTo(xScale(midPoint),0);
      context.strokeStyle="black";
      context.lineWidth=1;
      context.closePath();
      context.stroke();

      // RESET THE DASHED LINE CONFIGURATION.
      context.setLineDash([0, 0]);

  }

  function draw(options,mid_point) {
      context.clearRect(0, 0, fullWidth, fullHeight);
      context.moveTo(data[0][0].x, data[0][0].y);
      // data.sort(function(a,b){ return a[0].name.localeCompare(b[0].name); });
      for(var m = 0; m < data.length; m++){
          drawingOptions.lineColor = READ_COLORS[m];
          if(addition.line == 1) context.beginPath(); // SIGNAL LINE PLOT
          for(var i = 0; i < data[m].length; i++){
            // @MATT: Add an if statement here if you want to view only certain read. Ex: data[m][i] == '1182ad2e-10aa-421a-8fd3-39256b62a11b'

            // NEED TO CHANGE THIS CODE FOR READ COLORING.
            // if( (reA2012.exec(data[m][i].name) != null) && reA2012.exec(data[m][i].name)[0] == data[m][i].name ) drawingOptions.lineColor = 'red';
            // else drawingOptions.lineColor = 'blue';

            var point = data[m][i];
            var nextPoint = i < data[m].length-1 ? data[m][i+1] : 0;
            if(addition.line == 2) context.beginPath();  // STEP LINE PLOT
            drawVisualization(point,addition.width, nextPoint, drawingOptions, mid_point);
          }
      }
  }

  function drawVisualization(point, r, nextPoint,options, mPoint) {
    if(addition.non_basecalled || (!addition.non_basecalled && (point.x%1 == 0 && nextPoint.x %1 == 0)) ) { // NON BASECALLED
      var cx = xScale(point.x);
      var cy = yScale(point.y);

      var nX = xScale(nextPoint.x);
      var nY = yScale(nextPoint.y);


      if(addition.line != 0){
        context.lineTo(cx,cy); // Euclidean Plot
        if(addition.line == 2){ // Step Line Plot
          context.lineTo(nX,cy); // STEP LINE PLOT: line that goes horizontal
          context.lineTo(nX,nY); // STEP LINE PLOT: line that goes vertical.
        }
        context.lineWidth = addition.width;
        context.strokeStyle=options.lineColor;
        context.stroke();
      }

      // if(point.x %1 != 0){
      //   context.fillStyle="gray";
      // }else{
      //   context.fillStyle=options.lineColor;
      // }
      context.fillStyle=options.lineColor;
      context.beginPath();
      context.arc(cx, cy, r, 0, 2 * Math.PI);
      context.closePath();
      context.fill();


      if(point.x%1==0){
        var bcolor = "black";
        if(point.base == 'G') bcolor = 'orange';
        else if(point.base == 'C') bcolor = 'blue';
        else if(point.base == 'A') bcolor = 'green';
        else if(point.base == 'T') bcolor = 'red';
        context.font = "20px Arial"
        context.fillStyle=bcolor;
        context.fillText(point.base,xScale(point.x+0.5),yScale(-3.2));
        context.textAlign="center"
        context.fillStyle="gray";
      }
    }
  }
}
