/**
 * Djinn events JS lib
 */

// Use djinn namespace
if (djinn === undefined) {
    var djinn = {};
}


djinn.events = {};


/** 
 * Calculate end time for given start time in format HH:mm.
 */
djinn.events.calc_end_time = function(hourstr) {

  if (!hourstr || hourstr.len < 5) {
    return "";
  }

  var hour = parseInt(hourstr.substr(0, 3));

  if (hour >= 23) {
    return "00:00";
  }

  var newhour = "" + (hour + 1);

  if (newhour.length == 1) {
    newhour = "0" + "" + newhour;
  }

  return newhour + ":" + hourstr.substr(3);
};


$(document).ready(function() {
   
    $(document).on("click", "input[name='djinn_events_full_day']", function(e) {
        $("#id_start_time").toggle();
        $("#id_start_time").val("");        
        $("#id_end_time").toggle();
        $("#id_end_time").val("");                
      });    

    // Naive implementation that does string wise comparison
    $(document).on("change", ".event #id_start_date", function(e) {

        var startDate = $("#id_start_date").val();
        var endDate = $("#id_end_date").val();

        if ((!endDate) || endDate == $("#id_end_date").attr("placeholder")) {
          $("#id_end_date").val(startDate);
          $("#id_end_date").removeClass("placeholder");
        } else if (endDate < startDate) {
          $("#id_end_date").val(startDate);
          $("#id_end_date").removeClass("placeholder");
        }
      });

    // Naive implementation that does string wise comparison
    $(document).on("change", ".event #id_start_time", function(e) {

        var startTime = $("#id_start_time").val();
        var endTime = $("#id_end_time").val();
        
        if ((!endTime) || endTime == $("#id_end_time").attr("placeholder")) {
          $("#id_end_time").val(djinn.events.calc_end_time(startTime));
          $("#id_end_time").removeClass("placeholder");
        }

        if (endTime.substr(0, 3) <= startTime.substr(0, 3)) {
          $("#id_end_time").val(djinn.events.calc_end_time(startTime));
          $("#id_end_time").removeClass("placeholder");
        }
      });

    $(document).on("submit", "body.event.edit form", function(e) {
        $(e.currentTarget).find(":input").each(function() {
            if ($(this).val() == $(this).attr("placeholder")) {
              $(this).val("");
            }
          });
        return true;
      });
  });
