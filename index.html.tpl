<!DOCTYPE html>
<html lang="fr">
  <head>
    <meta charset="utf-8" />
    <title>Récapitulatif TG 2012</title>

    <!-- HTML 5 shim -->
    <!--[if lt IE 9]>
    <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->

    <!-- CSS styles -->
    <link href="lib/bootstrap/css/bootstrap.min.css" rel="stylesheet" />
  </head>

  <body class="container" data-spy="scroll">

    <style type="text/css">
      body
      {
        padding-top: 42px;
      }
      .turne-w
      {
        width: 80px;
        height: 20px;
        line-height: 20px;
        position: absolute;
        cursor: help;
      }
      .turne-h 
      {
        width: 15px;
        height: 90px;
        position: absolute;
        cursor: help;
      }
      .cuisine
      {
        width: 45px;
        height: 20px;
        line-height: 20px;
        position: absolute;
      }
      .toilettes
      {
        width: 15px;
        height: 80px;
        position: absolute;
      }
      .toilettes .turne-content
      {
        position: absolute;
        -webkit-transform: rotate(-90deg) translate(-40px, -15px);
        -moz-transform: rotate(-90deg) translate(-40px, -15px);
        transform: rotate(-90deg) translate(-40px, -15px);
      }
      .turne-h .turne-content
      {
        position: absolute;
        -webkit-transform: rotate(-90deg) translate(-50px, -16px);
        -moz-transform: rotate(-90deg) translate(-50px, -16px);
        transform: rotate(-90deg) translate(-50px, -16px);
      }
      .turne-h > .badge
      {
        position: absolute;
        right: 0;
        top: 0;
        -webkit-transform-origin: bottom;
        -moz-transform-origin: bottom;
        transform-origin: bottom;
        -webkit-transform: rotate(-90deg) translate(0, 10px);
        -moz-transform: rotate(-90deg) translate(0, 10px);
        transform: rotate(-90deg) translate(0, 10px);
      }
      .turne-w > .badge
      {
        position: absolute;
        right: 0;
        bottom: 3px;
      }
      .popover-inner
      {
        width: auto ! important;
        min-width: 280px;
        max-width: 500px;
      }
    </style>

    <header>
    <h1 class="page-header">Informations utiles au turnage 2012
      <small>Montrouge seulement, peut-être plus à venir</small>
    </h1>
    </header>

    <div class="navbar navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container">
          <a class="brand" href="#">
            Thurnes ENS
          </a>
          <ul class="nav">
            <li><a href="#MB">Tour B (Montrouge)</a></li>
            <li><a href="#MC">Tour C (Montrouge)</a></li>
          </ul>
        </div>
      </div>
    </div>

    <h4>Légende</h4>
    <span class="label" style="background-color: darkred">Très mauvais état</span>
    <span class="label" style="background-color: red">Mauvais état</span>
    <span class="label" style="background-color: orange">État moyen</span>
    <span class="label" style="background-color: green">Bon état</span>
    <span class="label" style="background-color: darkgreen">Très bon état</span>
    <span class="label" style="background-color: black">Garde-turne (indisponible)</span>
    <span class="label" style="background-color: grey">Pas de données disponibles</span>
    <br />
    <i class="icon-user"></i> Chambre occupée
    <i class="icon-ok"></i> Chambre libre

    <div style="height: 10px;"></div>

    {0}

    <div style="height: 200px;"></div>

    <!-- Scripts at end of page for faster loading -->
    <script src="lib/jquery/jquery-1.7.2.min.js"></script>
    <script src="lib/bootstrap/js/bootstrap.min.js"></script>
    <script type="text/javascript">
      $(document).ready(function()
          {
          $('[rel=popover]').popover({'placement': 'bottom'});
          });
</script>
  </body>
</html>
