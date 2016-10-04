//log(window.location.href)

queue()
.defer(d3.json, "/TwitterData/LessTweets")
.defer(d3.json, "/TwitterData/nodes")
.defer(d3.json, "/TwitterData/links")
.await(makeGraphs);
//.await(redraw);

var url = window.location.href;
var shared = false;
var clickedtweeter = null;
var clickedtweet = null;
var clickedtweetposition = null;
var res = url.split("http://localhost:5000/")
if(res[1]!="") {
  shared = true;
  var res2 = res[1].split("+");
  clickedtweeter = res2[0];
  clickedtweetposition=res2[1];
}


var retweeters = [];
var clickedtweeterposition = null;
var clickedtweettime = null;

function makeGraphs(error, tweets, nodes, links) {
  if(shared){
    for(var i = 0; i < Object.keys(tweets).length; i++){
      if(tweets[i]['i']==clickedtweetposition){
        clickedtweet = tweets[i]['text']
        log(clickedtweet)
      }
    }
    redraw();
  }

  var tweets = tweets;
  var nodes = nodes;
  var links = links;
  var svg = d3.select("#tweet-chart").append("svg")
  .attr("width", 1200)
  .attr("height", 700);
  drawSVG(svg, tweets, nodes, links);
};

function redraw(){
  queue()
  .defer(d3.json, "/TwitterData/LessTweets")
  .defer(d3.json, "/TwitterData/nodes")
  .defer(d3.json, "/TwitterData/links")
  .await(makeGraphs);

  function makeGraphs(error, tweets, nodes, links) {
    var tweets = tweets;
    var nodes = nodes;
    var links = links;
    retweetedBy = [];
    retweeters = [];
    if(clickedtweet!=null){
      jsontweetobject = null;
      for(var i = 0; i < Object.keys(tweets).length; i++){
        if(tweets[i]!=undefined){
          log(clickedtweet);
          if(tweets[i]['text']==clickedtweet){
            jsontweetobject = tweets[i]
          }
        }
      }
      for(var j = 0; j<jsontweetobject['rebloggedBy'].length; j++){
        retweetedBy.push(jsontweetobject['rebloggedBy'][j])
      }


      for(var i = 0; i < Object.keys(nodes).length; i++){
        if(nodes[i]!=undefined){
          if(nodes[i]['name']==clickedtweeter){
            clickedtweeterposition = nodes[i]['position']
          }
        }
      }

      for(var i = 0; i < Object.keys(nodes).length; i++){ 
        for(var j = 0; j<retweetedBy.length;j++){
          if(nodes[i]['position']==retweetedBy[j]){
            retweeters.push(nodes[i]['name']);
          }
        }
      }
      var retweeterstring = ""
      for(var j = 0; j<retweeters.length;j++){
        retweeterstring = retweeterstring+" "+ retweeters[j];
      }
      document.getElementById("name").innerHTML = clickedtweet;
      document.getElementById("handle").innerHTML = "Original Tweeter: ".bold() + clickedtweeter +"<br />" + "Time of tweet: ".bold() + jsontweetobject['created_at']
      +"<br />" + "Retweeted By: ".bold() + retweeterstring;
      for(var i = 0; i<retweetedBy.length; i++){
        links.push({"_id":123, "source":clickedtweeterposition,"target":retweetedBy[i],"value":2});
      }
    }

    d3.select("#tweet-chart").selectAll("svg").remove();
    var svg = d3.select("#tweet-chart").append("svg")
    .attr("width", 1200)
    .attr("height", 700);
    drawSVG(svg, tweets, nodes, links); 
  };
};

function clickedTweet(tweeter, tweet) {
  clickedtweeter = tweeter;
  clickedtweet = tweet;
  redraw();
  document.getElementById("name").innerHTML = "";
  document.getElementById("handle").innerHTML = "";
  document.getElementById("handlestring").innerHTML = "";
  document.getElementById("descstring").innerHTML = "";
  document.getElementById("desc").innerHTML = "";
  document.getElementById("urlstring").innerHTML = "";
  document.getElementById("url").innerHTML = "";
  document.getElementById("createdstring").innerHTML = "";
  document.getElementById("createdDate").innerHTML = "";
  document.getElementById("locationstring").innerHTML = "";
  document.getElementById("location").innerHTML = "";
  document.getElementById("tweetsstring").innerHTML = "";
  document.getElementById("tweets").innerHTML = "";

}

function refresh(){
  clickedtweeter = null;
  clickedtweet = null;
  clickedtweeterposition = null;
  var clickedtweetposition = null;

  redraw();
  document.getElementById("name").innerHTML ="Additional Information";
  document.getElementById("handle").innerHTML = "";
  document.getElementById("handlestring").innerHTML = "";
  document.getElementById("descstring").innerHTML = "";
  document.getElementById("desc").innerHTML = "";
  document.getElementById("urlstring").innerHTML = "";
  document.getElementById("url").innerHTML = "";
  document.getElementById("createdstring").innerHTML = "";
  document.getElementById("createdDate").innerHTML = "";
  document.getElementById("locationstring").innerHTML = "";
  document.getElementById("location").innerHTML = "";
  document.getElementById("tweetsstring").innerHTML = "";
  document.getElementById("tweets").innerHTML = "";
}

function share(){
  var origurl = String(window.location.href).split("\/")
  if(clickedtweet==null && clickedtweeter != null){
    alert(origurl[2]+"/"+clickedtweeter)
  }
  else if(typeof(jsontweetobject) != 'undefined'){
    if(clickedtweeter != null){
      alert(origurl[2]+"/"+clickedtweeter+"+"+jsontweetobject['i']);
    }
    else{
      alert("Nothing selected to share!");
    }
  }

  else{
    alert("Nothing selected to share!");
  }
}

function drawSVG(svg, tweets, nodes, links){
  var svg = svg;
  var tweets = tweets;
  var nodes = nodes;
  var links = links;
  var width = 1200;
  var height = 700;
  var json = JSON.stringify(tweets.text);
  var linecolour = d3.scale.category10();

  var force = d3.layout.force()
  .gravity(.05)
  .charge(-120)
  .linkDistance(50)
  .size([width, height]);

  var voronoi = d3.geom.voronoi()
  .x(function(d) { return d.x; })
  .y(function(d) { return d.y; })
  .clipExtent([[0, 0], [width, height]]);

  var link = svg.selectAll("line")
  .data(links)
  .enter().append("line")
  .attr("stroke-width", function(d) { return d.value; })
  .style("marker-end",  "url(#suit)")
  .attr("stroke",function(d) { return linecolour(d.value); });

  var node_drag = d3.behavior.drag()
  .on("dragstart", dragstart)
  .on("drag", dragmove)
  .on("dragend", dragend);

  function dragstart(d, i) {
    force.stop();
  }

  function dragmove(d, i) {
    d.px += d3.event.dx;
    d.py += d3.event.dy;
    d.x += d3.event.dx;
    d.y += d3.event.dy;
  }

  function dragend(d, i) {
    d.fixed = true; // of course set the node to fixed so the force doesn't include the node in its auto positioning stuff
    force.resume();
  }

  function releasenode(d) {
    d.fixed = false; // of course set the node to fixed so the force doesn't include the node in its auto positioning stuff
    force.resume();
  }



  function isFollower(d){
     for(var i = 0; i < Object.keys(links).length; i++){
      if(links[i]!=undefined){
        if(links[i]['source']==clickedtweeterposition){
        }
        if(links[i]['source']==clickedtweeterposition && links[i]['target']==d.position){
          if(links[i]['value']==1){

            return true;
          }
        }
      }
    }
    return false;
  }

  function didRetweet(d){

   for(var j = 0; j<retweeters.length;j++){
    if(retweeters[j]==d.name){
      return true;
    }
  }
  return false;
  }

  function setTweeter(d) {
    if(clickedtweet!=null){
      clickedtweet=null;
      clickedtweeter = d.name;
      redraw();
    }

    clickedtweeter = d.name;
    for(var i = 0; i < Object.keys(nodes).length; i++){
      if(nodes[i]!=undefined){
        if(nodes[i]['name']==clickedtweeter){
          clickedtweeterposition = nodes[i]['position']
        }
      }
    }



    d3.select("svg").selectAll("circle").transition().style("fill", "lightgrey");
    d3.select(this).select("circle").transition().style("fill", "lightsteelblue");

    d3.select("svg").selectAll("circle").each(function(d, i){
      for(var i = 0; i < Object.keys(links).length; i++){
        if(links[i]!=undefined){
          //log(JSON.stringify(links[i]))
          if(links[i]['source']['position']==clickedtweeterposition && links[i]['target']['position']==d.position){
            if(links[i]['value']==1){
              d3.select(this).transition().style("fill", "steelblue");
            }
          }
        }
      }
    })

    var tweetsofclickeduser = "";
    var j = 0;
    for(var i = 0; i < Object.keys(tweet).length; i++){
      if(tweets[i]!=undefined){
        if(tweets[i]['origin']==clickedtweeter){
          if(j<1){
            tweetsofclickeduser = "1. "+ tweets[i]['text']
          }
          else{
            var k = j + 1
            tweetsofclickeduser = tweetsofclickeduser +"<br />" + k+". "+ tweets[i]['text']
          }
          j=j+1;
        }

      }
    }
    document.getElementById("tweets").innerHTML = tweetsofclickeduser;
    $.get($SCRIPT_ROOT + '/_getuserdeets', {
      a: clickedtweeter
    }, function(data) {
      $("#name").text(data.name);
      $("#handle").text(data.handle);
      $("#handlestring").text("Handle: ");
      $("#desc").text(data.desc);
      $("#descstring").text("Description: ");
      $("#url").text(data.url);
      $("#urlstring").text("URL: ");
      $("#createdDate").text(data.createdDate);
      $("#createdstring").text("User Since: ");
      $("#location").text(data.location);
      $("#locationstring").text("Location: ");
      $("#comma").text("Comma: ");
      $("#tweetsstring").text("Tweets: ");
    });
    return false;
  }

  svg.append("defs").selectAll("marker")
  .data(["suit", "licensing", "resolved"])
  .enter().append("marker")
  .attr("id", function(d) { return d; })
  .attr("viewBox", "0 -5 10 10")
  .attr("refX", 25)
  .attr("refY", 0)
  .attr("markerWidth", 6)
  .attr("markerHeight", 6)
  .attr("orient", "auto")
  .append("path")
  .attr("d", "M0,-5L10,0L0,5 L10,0 L0, -5")
  .style("stroke", "#000000")
  .style("opacity", "0.6");

  var node = svg.selectAll("circle")
  .data(nodes)
  .enter().append("g")
  .attr("class", "node")
  .on('dblclick', setTweeter)
  .on('click', releasenode)
  .call(node_drag);

  var circle = node.append("circle")
  .attr("r", function(d) {return (d.amountoftweets + 1)*6; })
  .style("stroke", function(d){
    if(didRetweet(d)){
      return "Aquamarine"
    }
    else return "black"
  })
  .style("fill", function(d){
    if (d.name == clickedtweeter){
      return "lightsteelblue"
    }
    else if(isFollower(d)){
      return "steelblue"
    }
    else {
      return "lightgrey"
    }
  })

  var cell = node.append("path")
  .attr("class", "cell");

  var label = node.append("text")
  .attr("dy", ".35em")
  .text(function(d) {return d.name; });





  force
  .nodes(nodes)
  .links(links)
  .start();

  force.on("tick", function () {
    cell
    .data(voronoi(nodes))
    .attr("d", function(d) { return d.length ? "M" + d.join("L") : null; });

    link
    .attr("x1", function(d) { return d.source.x; })
    .attr("y1", function(d) { return d.source.y; })
    .attr("x2", function(d) { return d.target.x; })
    .attr("y2", function(d) { return d.target.y; });

    circle
    .attr("cx", function(d) { return d.x = Math.max((d.amountoftweets + 1) * 6, Math.min(width - (d.amountoftweets + 1) * 5, d.x)); })
    .attr("cy", function(d) { return d.y = Math.max((d.amountoftweets + 1) * 6, Math.min(height - (d.amountoftweets + 1) * 5, d.y)); });

    label
    .attr("x", function(d) { return d.x + 8; })
    .attr("y", function(d) { return d.y; });

  })



}

function log(msg) {
  setTimeout(function() {
    throw new Error(msg);
  }, 0);
};





