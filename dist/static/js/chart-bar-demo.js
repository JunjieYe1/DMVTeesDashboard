// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#292b2c';

// Bar Chart Example
function BuildChart(labels, values) {
  var ctx = document.getElementById("myBarChart");
  var myLineChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,//["January", "February", "March", "April", "May", "June"],
      datasets: [{
        label: "Revenue",
        backgroundColor: "rgba(2,117,216,1)",
        borderColor: "rgba(2,117,216,1)",
        data: values,
      }],
    },
    options: {
      responsive: true, // Instruct chart js to respond nicely.

      scales: {
        xAxes: [{
          time: {
            unit: 'month'
          },
          gridLines: {
            display: false
          },
          ticks: {
            maxTicksLimit: 6
          }
        }],
        yAxes: [{
          ticks: {
            min: 0,

            maxTicksLimit: 5
          },
          gridLines: {
            display: true
          }
        }],
      },
      legend: {
        display: false
      }
    }
  });
};


var table = document.getElementById('dataTable');
var json = []; // first row needs to be headers
var headers = [];
for (var i = 0; i < table.rows[0].cells.length; i++) {
    headers[i] = table.rows[0].cells[i].innerHTML.toLowerCase().replace(/ /gi, '');
}
// go through cells
for (var i = 0; i < table.rows.length; i++) {
    var tableRow = table.rows[i];
    var rowData = {};
    for (var j = 0; j < tableRow.cells.length; j++) {
        rowData[headers[j]] = tableRow.cells[j].innerHTML;
    }
    json.push(rowData);
}
console.log(json);
// Map json values back to label array
var labels = json.map(function (e) {
    return e.orderid;
});
console.log(labels);
// Map json values back to values array
var values = json.map(function (e) {
    return e.total.replace('$', '');
});
console.log(values);
var chart = BuildChart(barlabel, bardata);