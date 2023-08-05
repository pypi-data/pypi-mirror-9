jQuery(function($) {


  if ($('#listing-search').length > 0) {
    // Listing search viewlet.

    if ($('#listing-search div.results').length > 0) {
      // Hide the form when search was performed and show the edit form options link.
      $('div.results > form').hide();
      $('div.results #show-form').show().click(function(event) {
        event.preventDefault();
        $('div.results > form').slideToggle();
      });
    }
  }

  if ($('#listing-images .thumbnails').length > 0) {
    // Build JS Gallery for listing detail view.

    // Load the theme ones more. This is necessary for mobile devices.
    Galleria.loadTheme('++resource++plone.mls.listing.javascript/classic/galleria.classic.min.js');
    $('#listing-images a.preview').replaceWith('<div id="galleria"></div>');

    // Hide the thumbnails
    $('#listing-images .thumbnails').hide();

    // Initialize Galleria.
    var galleria_obj = $('#galleria').galleria({
      dataSource: '.thumbnails',
      width: 410,
      height: 400,
      preload: 3,
      transition: 'fade',
      transitionSpeed: 1000,
      autoplay: 5000
    });
  }


  if ($('#content-views #contentview-local-mls-agency-info').length > 0) {
    // Show the local agency information form with a nice overlay.
    $('#content-views #contentview-local-mls-agency-info > a').prepOverlay({
      subtype: 'ajax',
      filter: '#content>*',
      formselector: '#content-core > form',
      noform: 'reload',
      closeselector: '[name="form.buttons.cancel"]'
    });
  }

  if ($('#content-views #contentview-listing-collection-config').length > 0) {
    // Show the listing search configuration form with a nice overlay.
    $('#content-views #contentview-listing-collection-config > a').prepOverlay({
      subtype: 'ajax',
      filter: '#content>*',
      formselector: '#content-core > form',
      noform: 'reload',
      closeselector: '[name="form.buttons.cancel"]'
    });
  }

  if ($('#content-views #contentview-listing-search-config').length > 0) {
    // Show the listing search configuration form with a nice overlay.
    $('#content-views #contentview-listing-search-config > a').prepOverlay({
      subtype: 'ajax',
      filter: '#content>*',
      formselector: '#content-core > form',
      noform: 'reload',
      closeselector: '[name="form.buttons.cancel"]'
    });
  }

  if ($('#content-views #contentview-recent-listings-config').length > 0) {
    // Show the listing search configuration form with a nice overlay.
    $('#content-views #contentview-recent-listings-config > a').prepOverlay({
      subtype: 'ajax',
      filter: '#content>*',
      formselector: '#content-core > form',
      noform: 'reload',
      closeselector: '[name="form.buttons.cancel"]'
    });
  }

  if ($('.portletQuickSearch').length > 0) {

    if ($('.portletQuickSearch input[name=form.widgets.object_type:list]:checked').length > 0) {
      $('.portletQuickSearch #formfield-form-widgets-object_type > .collapser').click();
    }

    if ($('.portletQuickSearch input[name=form.widgets.location_type:list]:checked').length > 0) {
      $('.portletQuickSearch #formfield-form-widgets-location_type > .collapser').click();
    }

    if ($('.portletQuickSearch input[name=form.widgets.geographic_type:list]:checked').length > 0) {
      $('.portletQuickSearch #formfield-form-widgets-geographic_type > .collapser').click();
    }

    if ($('.portletQuickSearch input[name=form.widgets.view_type:list]:checked').length > 0) {
      $('.portletQuickSearch #formfield-form-widgets-view_type > .collapser').click();
    }

    if ($('.portletQuickSearch input[name=form.widgets.ownership_type:list]:checked').length > 0) {
      $('.portletQuickSearch #formfield-form-widgets-ownership_type > .collapser').click();
    }

    if ($('.portletQuickSearch input[name=form.widgets.air_condition:list]:checked').val() != '--NOVALUE--') {
      $('.portletQuickSearch #formfield-form-widgets-air_condition > .collapser').click();
    }

    if ($('.portletQuickSearch input[name=form.widgets.pool:list]:checked').val() != '--NOVALUE--') {
      $('.portletQuickSearch #formfield-form-widgets-pool > .collapser').click();
    }

    if ($('.portletQuickSearch input[name=form.widgets.jacuzzi:list]:checked').val() != '--NOVALUE--') {
      $('.portletQuickSearch #formfield-form-widgets-jacuzzi > .collapser').click();
    }
  }

});
