/**
 * Djinn Announcements JS lib.
 */

// Use djinn namespace
if (djinn == undefined) {
  var djinn = {}
}


djinn.hide_announcements_alert = function() {
  $("#announcements-alert").hide();
  $("#announcementlist").show();
};


$(document).ready(function() {

    $(document).on("click", ".remove-update", function(e) {
        
        var tgt = $(e.target);
        var rec = tgt.parents(".update").eq(0);

        rec.hide();
        rec.find("input[name$=DELETE]").click();

        e.preventDefault();
      });
  })
