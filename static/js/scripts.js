// Mobile View -- menu slide up and down when the "Menu" button is pressed
$(".logo button").on("click", function(){
    $(".sidebar-items").slideToggle();
})

// On Dashboard - Month status section -> to show the status
var textValue = $(".progress-bar").text();
var newValue = parseInt(textValue.replace("%", ""));
if (newValue === 100) {
    $("#monthProgress h5").append('<span class="badge text-bg-success" style="float:right;">Ended</span>');
} else if (newValue < 100) {
    $("#monthProgress h5").append('<span class="badge text-bg-secondary" style="float:right;">In progress</span>');
} else {
    $("#monthProgress h5").append('<span class="badge text-bg-light" style="float:right;">Not started yet</span>');
}

// Show days used for a Time Of Request - Time Off Request TAB
function getBusinessDatesCount(startDate, endDate) {
    let count = 0;
    const curDate = new Date(startDate.getTime());
    while (curDate <= endDate) {
        const dayOfWeek = curDate.getDay();
        if(dayOfWeek !== 0 && dayOfWeek !== 6) count++;
        curDate.setDate(curDate.getDate() + 1);
    }
    return count;
}

$("input#from, input#to").on("change", function(){
    var startDate = new Date($("#from").val());
    var endDate = new Date($("#to").val());
    var result = getBusinessDatesCount(startDate,endDate);
    $("#days").val(result);
});

// Filter of Ticket from History Request
function show(status){
  var rows = $("#requestTable tr").length;
  for (i = 0; i <= rows; i++) {
    var firstRow = $("#requestTable tr")[i];
    var tableStatus = firstRow.lastElementChild.innerText;
    console.log(tableStatus);
    if (status == 0) {
      $("#requestTable tr").eq(i).show();
    } else {
      if (status != tableStatus) {
        $("#requestTable tr").eq(i).hide();
      } else {
        $("#requestTable tr").eq(i).show();
      };
    };
  };
};
$("#requestsFilter").on("change", function(){
  console.log($(this).val());
  var status = $(this).val();
  show(status);
});
var x = $("#requestTable #status").text();
for (i = 0; i <= $("#requestTable #status").text().length; i++){
    console.log(x[i])
    if (x[i] == 1) {
        $("#status span").eq(i).addClass("text-bg-warning");
    } else if (x[i] == 6) {
        $("#status span").eq(i).addClass("text-bg-success");
    } else {
        $("#status span").eq(i).addClass("text-bg-danger");
    }
}

$("#fileUpload").click(function(){
    $("#upload-file").click();
});

$("#editIcon").click(function(){
    $("#changeAvatarModal").click();
})


