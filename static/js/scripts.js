
//function email() {
//   let first = document.getElementById("first").value;
//   let last = document.getElementById("last").value;
//   document.getElementById("demo").innerHTML = first.toLowerCase() + "." + last.toLowerCase()  + "@arch-dev.com";
//}
//
//      google.charts.load('current', {'packages':['bar']});
//      google.charts.setOnLoadCallback(drawStuff);
//
//      function drawStuff() {
//        var data = new google.visualization.arrayToDataTable([
//          ['User', 'Percentage'],
//          ["Andrei", 100],
//          ["Diana", 20],
//          ["Elena", 12],
//          ["Marius", 10],
//          ['Other', 3]
//        ]);
//
//        var options = {
//          width: 800,
//          legend: { position: 'none' },
//          chart: {
//            title: 'Chess opening moves',
//            subtitle: 'popularity by percentage' },
//          axes: {
//            x: {
//              0: { side: 'top', label: 'Completation for March'} // Top x-axis.
//            }
//          },
//          bar: { groupWidth: "90%" }
//        };
//
//        var chart = new google.charts.Bar(document.getElementById('top_x_div'));
//        // Convert the Classic options to Material options.
//        chart.draw(data, google.charts.Bar.convertOptions(options));
//      };