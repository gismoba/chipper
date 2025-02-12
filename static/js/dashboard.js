const total_views = document.getElementById('total-views');
const total_views_pie = document.getElementById('total-views-pie');

var views_1 = document.querySelector('.views_1').textContent.trim()
var views_2 = document.querySelector('.views_2').textContent.trim()
var views_3 = document.querySelector('.views_3').textContent.trim()
var views_4 = document.querySelector('.views_4').textContent.trim()
var views_5 = document.querySelector('.views_5').textContent.trim()
var views_6 = document.querySelector('.views_6').textContent.trim()
var views_7 = document.querySelector('.views_7').textContent.trim()
var views_8 = document.querySelector('.views_8').textContent.trim()
var views_9 = document.querySelector('.views_9').textContent.trim()
var views_10 = document.querySelector('.views_10').textContent.trim()
var views_11 = document.querySelector('.views_11').textContent.trim()
var views_12 = document.querySelector('.views_12').textContent.trim()

new Chart(total_views, {
  type: 'line',
  data: {
    labels: [
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'June',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec',],
    datasets: [{
      label: 'Total Views',
      data: [views_1,
             views_2,
             views_3,
             views_4,
             views_5,
             views_6,
             views_7,
             views_8,
             views_9,
             views_10,
             views_11,
             views_12],
      borderWidth: 2
    }]
  },
  options: {
    scales: {
      y: {
        min: 0
      }
    },
    spanGaps: true
  }
});

const payoutData = {
  labels: [
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'June',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec',
  ],
  datasets: [{
    label: 'Total Views',
    data: [views_1,
      views_2,
      views_3,
      views_4,
      views_5,
      views_6,
      views_7,
      views_8,
      views_9,
      views_10,
      views_11,
      views_12],
    backgroundColor: [
      '#257CFD',
      '#F3894F',
      '#ABABAB',
      '#FFC33D',
      '#537DC4',
      '#78B25E',
      '#376C95',
      '#508085',
      '#e31809',
      '#e36f09',
      '#ff9ce4',
      '#7d5572',
    ],
    hoverOffset: 4
  }]
};
new Chart(total_views_pie, {
type: 'pie',
data:payoutData,
  options: {
    responsive: true,
    maintainAspectRatio: false
}
});