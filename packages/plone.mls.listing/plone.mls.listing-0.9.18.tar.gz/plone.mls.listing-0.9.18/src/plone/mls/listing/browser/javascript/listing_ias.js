jQuery(function($) {

  if ($('#listing-collection').length > 0) {
    // Infinite Ajax Scroll for listing collection results.
    $.ias({
      container : "#listing-collection",
      item: ".tileItem",
      pagination: "#content .listingBar",
      next: ".next a",
      loader: "spinner.gif"
    });
  }

  if ($('#listing-search').length > 0) {
    // Infinite Ajax Scroll for search results.
    $.ias({
      container : '#listing-search',
      item: '.tileItem',
      pagination: '#content .listingBar',
      next: '.next a',
      loader: 'spinner.gif'
    });
  }

  if ($('#recent-listings').length > 0) {
    // Infinite Ajax Scroll for recent listings.
    $.ias({
      container : "#recent-listings",
      item: ".tileItem",
      pagination: "#content .listingBar",
      next: ".next a",
      loader: "spinner.gif"
    });
  }
});
