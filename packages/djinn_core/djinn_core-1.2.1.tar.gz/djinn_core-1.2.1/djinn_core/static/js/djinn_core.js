/**
 * Djinn core defines some handlers for inline editing.
 */

// Use djinn namespace
if (djinn === undefined) {
  var djinn = {};
}


djinn.settings = {
  ALERT_MAP: {25: "success"}
};


/**
 * Get the target of the given element as defined in the 'target' attribute.
 * If that is not there, return the element itself.
 * @param elt jQuery wrapped element
 */
djinn.get_target = function(elt) {

  if (elt.attr("target")) {
    return $(elt.attr("target"));
  } else {
    return elt;
  }
};


djinn.handle_messages = function() {

  var name = "messages=";
  var ca = document.cookie.split(';');
  var messages = "";

  for(var i=0; i<ca.length; i++) {

    var c = ca[i].trim();
    if (c.indexOf(name) === 0) {
      messages = c.substring(name.length, c.length - 1);
    }
  }

  if (messages) {

    messages = messages.split("$")[1].replace(/\\054/g, ',').replace(/\\"/g, '"');

    messages = JSON.parse(messages);

    djinn.show_message(messages[0][3],
                       djinn.settings.ALERT_MAP[messages[0][2]] || "info");
  }
};


djinn.hide_message = function() {

  $("#message").hide("slow");
};


djinn.show_message = function(mesg, type) {

  $("body").append('<div id="message" class="alert alert-' + type + '"><a class="close" data-dismiss="alert">&times;</a>' + mesg + '</div>');

  setTimeout(djinn.hide_message, 5000);

  $("#message").alert();
};


/**
 * Handle links with the update inline-class. This assumes that a GET
 * can be called with the URL provided in the href attribute. The
 * response should be either status 202 in case of errors, or 200.
 * @param e The event that triggered the call.
 */
djinn.update_inline = function(e) {

  var link = $(e.currentTarget);
  var target = djinn.get_target(link);

  e.preventDefault();

  $.get(link.attr("href"), function(data, status, xhr) {

    if (xhr.status == 202) {
      // nasty
    } else {
      target.replaceWith(data);
    }

    djinn.handle_messages();
  });
};


/**
 * Try to repair crappy URL's.
 * @param url URL to repair
 * @param proto Protocol to repair for. Default is http.
 */
djinn.normalizeURL = function(url, proto) {

    if (proto == "email") {
        if (!url.startsWith("mailto:")) {
            url = "mailto:" + url;
        }
    } else if (proto == "https") {
        if (!url.startsWith("https://")) {
            url = "https://" + url;
        }
    } else {
      if (!(url.startsWith("http://") || url.startsWith("https://"))) {
          url = "http://" + url;
      }
    }

    return url;
};


$(document).ready(function() {

  $(document).on("click", "a.update-inline", djinn.update_inline);

  // Prevent double clicks, when the link or button has the class
  // 'protected'. The actual handling of the event furtheron is
  // responsible for removing the disabled class if need be. Submit
  // buttons should not be protected, since that results in not
  // submitting the form at all in some browsers...
  //
  $(document).on("click",
                 "input.protected,a.protected,button.protected",
                 function(e) {

                   // this is a workaround for browsers not sending data of
                   // disabled fields/buttons in submit (conform specs, by
                   // the way)
                   // the workaround adds a hidden field with name/value of
                   // the submit button
                   $('<input>').attr({
                        type: 'hidden',
                        value: e.currentTarget.value,
                        name: e.currentTarget.name
                    }).appendTo(e.currentTarget.form);

                   if ($(e.currentTarget).is([type=submit])) {
                     return;
                   }
                   $(e.currentTarget).addClass("disabled");
                 });
  
  // Do nothing...
  $(document).on("click", ".protected.disabled", function(e) {
    e.preventDefault();
  });

  // Protect form from double submit
  $(document).on("submit", "form.protected", function(e) {

    if ($(e.target).is(".disabled")) {
      e.preventDefault();

      return false;
    }

    var disable_expr = ".form-actions a,.form-actions button,[type=submit]";

    $(e.target).addClass("disabled");
    $(e.target).find(disable_expr).addClass("disabled");
  });
});
