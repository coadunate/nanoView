function performClick(dir, ref, sam, name) {
   var xhttp = new XMLHttpRequest();
   var dir = document.getElementById(dir);
   var ref = document.getElementById(ref);
   var sam = document.getElementById(sam);
   var name = document.getElementById(name);

   var dirPath = dir.value;
   var refPath = ref.value;
   var samPath = sam.value;
   var projectName = name.value;

   // var paths = [ { "dir_path" : dirPath }, { "ref_path" : refPath },
   //     { "bam_path" : samPath }, {"project_name" : projectName} ];
   var paths = "name=" + projectName + "&directory=" + dirPath + "&ref=" + refPath + "&sam=" + samPath;


   xhttp.open("GET", "http://127.0.0.1:5000/generatejson/"+paths, true);
   xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
   // xhttp.send(paths);
   xhttp.onload = function () {
     console.log(xhttp.responseText);
   };
   xhttp.send();
   // xhttp.send("name=hi&directory=tdowhy&ref=root&sam=home");
   // console.log(paths)

   // event.preventDefault();

   // console.log(xhttp.responseText)

   // call js class with sam file or store variable

}


function getProjects() {
  var xhttp = new XMLHttpRequest();
  xhttp.open("GET", "http://127.0.0.1:5000/getprojects/", true);
  xhttp.setRequestHeader("Content-Type", "application/json");
  xhttp.onload = function() {
    var projects = JSON.parse(xhttp.responseText);
    // console.log(projects);
    // var wrapper = $('#wrapper'), container;
    for (var key in projects){
      var div = document.createElement("option");
      div.innerHTML = projects[key];
      div.value = projects[key];
      document.getElementById("existing").appendChild(div);
    }
  }
  xhttp.send();

  // event.preventDefault();
}

function test() {
  var xhttp = new XMLHttpRequest();
  xhttp.open("GET", "http://127.0.0.1:5000/test1/", true);
  xhttp.onload = function() {
    // var projects = JSON.parse(xhttp.responseText);
    console.log(xhttp.responseText);
    // var wrapper = $('#wrapper'), container;
  }
  xhttp.send();

  // event.preventDefault();
}

// $(document).ready(function() {
//   var xhttp = new XMLHttpRequest();
//   xhttp.open("GET", "http://127.0.0.1:5000/getprojects/", true);
//   xhttp.onload = function() {
//     var projects = JSON.parse(xhttp.responseText);
//     // console.log(projects);
//     // var wrapper = $('#wrapper'), container;
//     for (var key in projects){
//       var div = document.createElement("option");
//       div.innerHTML = projects[key];
//       div.value = projects[key];
//       document.getElementById("existing").appendChild(div);
//     }
//   }
//   xhttp.send();
//
//   // event.preventDefault();
// });
