(function ($) {
  /**
   * Patch TOC list.
   *
   * Will mutate the underlying span to have a correct ul for nav.
   *
   * @param $span: Span containing nested UL's to mutate.
   * @param minLevel: Starting level for nested lists. (1: global, 2: local).
   */
  var patchToc = function ($ul, minLevel) {
    var findA,
      patchTables,
      $localLi;

    // Find all a "internal" tags, traversing recursively.
    findA = function ($elem, level) {
      level = level || 0;
      var $items = $elem.find("> li > a.internal, > ul, > li > ul");

      // Iterate everything in order.
      $items.each(function (index, item) {
        var $item = $(item),
          tag = item.tagName.toLowerCase(),
          $childrenLi = $item.children('li'),
          $parentLi = $($item.parent('li'), $item.parent().parent('li'));

        // Add dropdowns if more children and above minimum level.
        if (tag === 'ul' && level >= minLevel && $childrenLi.length > 0) {
          $parentLi
            .addClass('dropdown-submenu')
            .children('a').first().attr('tabindex', -1);

          $item.addClass('dropdown-menu');
        }

        findA($item, level + 1);
      });
    };

    findA($ul);
  };

  /**
   * Patch all tables to remove ``docutils`` class and add Bootstrap base
   * ``table`` class.
   */
  patchTables = function () {
    $("table.docutils")
      .removeClass("docutils")
      .addClass("table")
      .attr("border", 0);
  };

  $(window).load(function () {
    /*
     * Scroll the window to avoid the topnav bar
     * https://github.com/twbs/bootstrap/issues/1768
     */
    if ($("#navbar.navbar-fixed-top").length > 0) {
      var navHeight = $("#navbar").height(),
        shiftWindow = function() { scrollBy(0, -navHeight - 10); };

      if (location.hash) {
        setTimeout(shiftWindow, 1);
      }

      window.addEventListener("hashchange", shiftWindow);
    }
  });

  patch_args = function(element) {
    element.find('dl.docutils').addClass('list-group').css('padding-top', '15px').each(function() {
        $(this).children(':even').each(function() {
            $(this).add($(this).next()).wrapAll('<li class="list-group-item"></li>');
            });
        $(this).find('p').addClass('panel-text');
        }).find('dd').css("padding-left", "20px");
    element.find('dl.docutils').parent().each(function() {
        $(this).parent().filter('blockquote').children('div:first').unwrap().end();
    });
  };

  $(document).ready(function () {
    // Add styling, structure to TOC's.
    $(".dropdown-menu").each(function () {
      $(this).find("ul").each(function (index, item){
        var $item = $(item);
        $item.addClass('unstyled');
      });
    });

    // Global TOC.
    if ($("ul.globaltoc li").length) {
      patchToc($("ul.globaltoc"), 1);
    } else {
      // Remove Global TOC.
      $(".globaltoc-container").remove();
    }

    // Local TOC.
    $(".bs-sidenav ul").addClass("nav nav-list");
    $(".bs-sidenav > ul > li > a").addClass("nav-header");

    
    // back to top
    setTimeout(function () {
      var $sideBar = $('.bs-sidenav');

      $sideBar.affix({
        offset: {
          top: function () {
            var offsetTop      = $sideBar.offset().top;
            var sideBarMargin  = parseInt($sideBar.children(0).css('margin-top'), 10);
            var navOuterHeight = $('#navbar').height();

            return (this.top = offsetTop - navOuterHeight - sideBarMargin);
          }
        , bottom: function () {
            // add 25 because the footer height doesn't seem to be enough
            return (this.bottom = $('.footer').outerHeight(true) + 25);
          }
        }
      });
    }, 100);
    

    // Local TOC.
    patchToc($("ul.localtoc"), 2);

    // Mutate sub-lists (for bs-2.3.0).
    $(".dropdown-menu ul").not(".dropdown-menu").each(function () {
      var $ul = $(this),
        $parent = $ul.parent(),
        tag = $parent[0].tagName.toLowerCase(),
        $kids = $ul.children().detach();

      // Replace list with items if submenu header.
      if (tag === "ul") {
        $ul.replaceWith($kids);
      } else if (tag === "li") {
        // Insert into previous list.
        $parent.after($kids);
        $ul.remove();
      }
    });

    // Add divider in page TOC.
    $localLi = $("ul.localtoc li");
    if ($localLi.length > 2) {
      $localLi.first().after('<li class="divider"></li>');
    }

    // Patch tables.
    patchTables();

    // ========================================================================
    // Admonition Styles
    // ========================================================================

    // Add Note, Warning styles. (BS v2,3 compatible).
    $('.admonition').addClass('panel panel-info')
      .filter('.note')
        .removeClass('panel-info')
        .addClass('panel-primary').end()
      .filter('.warning, .caution')
        .removeClass('panel-info')
        .addClass('panel-warning').end()
      .filter('.error, .danger')
        .removeClass('panel-info')
        .addClass('panel-danger').end();
    
    // Format the inside of the Note/Warning panels correctly
    $('.admonition').each(function() {
        $(this).children('.admonition-title').replaceWith('<div class="panel-heading"><h3 class="panel-title">' + $(this).children('.admonition-title').text() + '</h3></div>');
        $(this).children('p').addClass('panel-text');
        $(this).children('div:first').siblings().wrapAll('<div class="panel-body"></div>');
        });

    // ========================================================================
    // Version Styles
    // ========================================================================

    $('.versionadded').each(function() {
        var versionMod = $(this).find('.versionmodified').text();
        var firstLine = $(this).children('p:first').clone().children().remove().end().text();
        
        $(this).children('p:first').replaceWith('<div class="panel-heading"><h3 class="panel-title">' + versionMod + '</h3></div>');
        $(this).children('div:first').after('<p>' + firstLine + '</p>');
        $(this).children('p').addClass('panel-text');
        $(this).children('div:first').siblings().wrapAll('<div class="panel-body"></div>');
        $(this).addClass('panel panel-success');
        });
    
    $('.versionchanged').each(function() {
        var versionMod = $(this).find('.versionmodified').text();
        var firstLine = $(this).children('p:first').clone().children().remove().end().text();
        
        $(this).children('p:first').replaceWith('<div class="panel-heading"><h3 class="panel-title">' + versionMod + '</h3></div>');
        $(this).children('div:first').after('<p>' + firstLine + '</p>');
        $(this).children('p').addClass('panel-text');
        $(this).children('div:first').siblings().wrapAll('<div class="panel-body"></div>');
        $(this).addClass('panel panel-info');
        });
    
    $('.deprecated').each(function() {
        var versionMod = $(this).find('.versionmodified').text();
        var firstLine = $(this).children('p:first').clone().children().remove().end().text();
        
        $(this).children('p:first').replaceWith('<div class="panel-heading"><h3 class="panel-title">' + versionMod + '</h3></div>');
        $(this).children('div:first').after('<p>' + firstLine + '</p>');
        $(this).children('p').addClass('panel-text');
        $(this).children('div:first').siblings().wrapAll('<div class="panel-body"></div>');
        $(this).addClass('panel panel-danger');
        });

    // ========================================================================
    // Misc
    // ========================================================================
    
    // Remove the Stupid header links
    $('.headerlink').remove();

    // Inline code styles to Bootstrap style.
    $('tt.docutils.literal').not(".xref").each(function (i, e) {
      // ignore references
      if (!$(e).parent().hasClass("reference")) {
        $(e).replaceWith(function () {
          return $("<code />").html($(this).html());
        });
      }});

    // Update sourcelink to remove outerdiv (fixes appearance in navbar).
    var $srcLink = $(".nav #sourcelink");
    $srcLink.parent().html($srcLink.html());
    
    // ========================================================================
    // Code Display
    // ========================================================================

    /* Uncomment this code display if you're using this javascript in an
    octopress blog. Otherwise it will just mess up the html display. */

    /*
    // Code Without Line Numbers
    $('.highlight').each(function() {
        if ( !($(this).parent().first().hasClass('code')) ) {
            var codeType = $(this).parent().first().attr("class").replace('highlight-', '');
            
            $(this).wrap('<figure class="code panel panel-default"></figure>');
            $(this).children()
                .wrap('<table><tbody><tr><td class="code"></td></tr></tbody></table>')
                .wrapInner('<code class="' + codeType + '"></code>')
                .find('.go').addClass('s').removeClass('go');
          };
    });

    // Code With Line Numbers
    $('.highlighttable').each(function() {
        var codeType = $(this).parent().first().attr("class").replace('highlight-', '');
        
        $(this).wrap('<figure class="code panel panel-default"><div class="highlight"></div></figure>');
        $(this).find('.linenos').addClass('gutter').find('pre').addClass('line-numbers').wrapInner('<span class="line-number"></span>');
        $(this).find('.highlight').children().unwrap().wrapInner('<code class="' + codeType + '"></code>');
    });

    // Highlight Lines correctly
    $('.hll').addClass('line marked');
    */
    
    // ========================================================================
    // AutoDoc
    // ========================================================================
    
    // Module Wrapping
    $('.section').each(function() {
        if ($(this).attr('id').indexOf('module') != -1) {
            var module = $(this).children('.section');
            
            module.addClass('panel panel-default');
            module.children(':header').addClass('panel-title').wrap('<div class="panel-heading"></div>');
            module.children('div:first').siblings().wrapAll('<div class="panel-body"></div>');
            module.find('p').addClass('panel-text');
            patch_args(module);
        };
    });
    
    // Class Wrapping
    $('.class').each(function() {
        $(this).addClass('panel panel-success');
        $(this).children('dt')
            .addClass('panel-title')
            .wrap('<div class="panel-heading"></div>')
            .children('em:not(.property)').addClass('badge').css('font-size', '0.9em');
        $(this).children('dd')
            .addClass('panel-body')
            .children('dl.docutils').children().unwrap();
        $(this).find('p').addClass('panel-text');
        patch_args($(this));
    });
    
    // Function Wrappings
    $('.function').each(function() {
        $(this).addClass('panel panel-info');
        $(this).children('dt')
            .addClass('panel-title')
            .wrap('<div class="panel-heading"></div>')
            .children('em:not(.property)').addClass('badge').css('font-size', '0.9em');
        $(this).children('dd')
            .addClass('panel-body')
            .children('dl.docutils').children().unwrap();
        $(this).find('p').addClass('panel-text');
        patch_args($(this));
    });

    // Method Wrappings
    $('.method').each(function() {
        $(this).addClass('panel panel-info');
        $(this).children('dt')
            .addClass('panel-title')
            .wrap('<div class="panel-heading"></div>')
            .children('em:not(.property)').addClass('badge').css('font-size', '0.9em');
        $(this).children('dd')
            .addClass('panel-body')
            .children('dl.docutils').children().unwrap();
        $(this).find('p').addClass('panel-text');
        patch_args($(this));
    });

    // Attribute Wrappings
    $('.attribute').each(function() {
        $(this).addClass('panel panel-warning');
        $(this).children('dt')
            .addClass('panel-title')
            .wrap('<div class="panel-heading"></div>')
            .children('em:not(.property)').addClass('badge').css('font-size', '0.9em');
        $(this).children('dd')
            .addClass('panel-body')
            .children('dl.docutils').children().unwrap();
        $(this).find('p').addClass('panel-text');
        patch_args($(this));
    });
    
    // Classifier Styling for Args
    $('.classifier').addClass('label label-danger').css('font-size', '.86em');
    $('.classifier-delimiter').addClass('badge');
    
  });
}(window.$jqTheme || window.jQuery));