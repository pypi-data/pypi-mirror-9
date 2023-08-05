/**
 * Link widget JS
 */

if (djinn === undefined) {
    var djinn = {};
}


if (djinn.forms === undefined) {
  djinn.forms = {};
}


djinn.forms.link = {};


/*
 * Handler for click event on modal window link.
 * @param e Event
 */
djinn.forms.link.handleClick = function(e) {

  e.preventDefault();
  e.stopPropagation();
  
  var search_item = $(e.currentTarget);
  var anchor = search_item.find('h1 a');
  
  var value = search_item.data("url") || anchor.attr("href");
  var title = search_item.data("title") || anchor.text().trim();
  
  var form = $("#link_popup_form");

  form.find('input[name=url]').val(value);
  form.find('input[name=title]').val(title);
  form.find('input[name=cid]').val(search_item.data("cid"));
  form.find('input[name=ctype]').val(search_item.data("ctype"));

  var popup_title = gettext('Je hebt de link naar "%s" geselecteerd. Klik op “Link toevoegen” om de link in de pagina te plaatsen.');
  popup_title = interpolate(popup_title, [title]);

  // clean up old alert
  form.find('.link-added-alert').remove();
  form.find('input[name=url]').after('<span class="alert alert-info link-added-alert">' + popup_title + '</a>');
  $('.modal-add-link').toggleClass('open-modal-add-link');
};


$(document).ready(function() {

  /**
   * Handle the click on the link that should show the actual search
   * popup.
   */
  $(document).on("click", ".link a", function(e) {

    e.preventDefault();

    var link = $(e.currentTarget);
    var widget = link.parents(".link");

    $.get(link.attr("href"), function(data) {

      var modal = djinn.contenttypes.show_modal(data);

      modal.on("submit", "#link_popup_form", function(e) {

        e.preventDefault();
    
        var form = e.currentTarget;
    
        var url = form.url.value;
        var title = form.title.value;
    
        if (url) {
          
          if (!url.startsWith("mailto:") && !url.startsWith("/") &&
              !url.startsWith("urn:")) {
            url = djinn.normalizeURL(form.url.value, "http");
          }

          url = url + "::";

          widget.find("input").val(url);
          widget.find(".link_label").html(title || url);
        }

        modal.modal("hide");
      });
    });

  });

  // Don't follow links in link popup
  $(document).on('click', '#contentlinks .search-item a', function(e) {
    e.preventDefault();
  });

  $(document).on('click', '#contentlinks .search-item', 
                 djinn.forms.link.handleClick);
  
});
