<!DOCTYPE html>
<html lang="fr">
  <head>
    <meta charset="utf-8" />
    <title>Récapitulatif TG 2014</title>

    <!-- HTML 5 shim -->
    <!--[if lt IE 9]>
    <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->

    <!-- CSS styles -->
    <link href="lib/bootstrap/css/bootstrap.min.css" rel="stylesheet" />
  </head>

  <body class="container">

    <style type="text/css">
      body
      {
        padding-top: 42px;
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

      .turne-h .turne-content
      {
        position: absolute;
        -webkit-transform: rotate(-90deg) translate(-50px, -16px);
        -moz-transform: rotate(-90deg) translate(-50px, -16px);
        transform: rotate(-90deg) translate(-50px, -16px);
      }
      .turne-w > .badge
      {
        position: absolute;
        right: 0;
        bottom: 3px;
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
      .popover-inner
      {
        width: auto ! important;
        min-width: 280px;
        max-width: 500px;
      }
      .mezza
      {
        border: 2px solid #cfa700;
        box-shadow: 0 0 0.7em #cfa700;
        border-radius: 4px;
        margin: -2px;
      }
    </style>

    <header>
    <h1 class="page-header">Informations utiles au thurnage 2014 <small>Montrouge (175 thurnes disponibles)</small></h1>
    </header>

    <div class="navbar navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container">
          <a class="brand" href="#">
            Thurnes ENS
          </a>
          <ul class="nav">
	    <li><a href="Ulm.html">Ulm (115 thurnes)</a></li>
	    <li><a href="Jourdan.html">Jourdan (34 thurnes)</a></li>
            <li><a href="Montrouge.html">Montrouge (175 thurnes)</a></li>
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
    <span class="label mezza" style="background-color: green;">Présence de mezzanine</span>
    <span class="label" style="background-color: grey">Pas de données récentes</span>
    <br />
    <i class="icon-user"></i> Chambre occupée
    <i class="icon-ok"></i> Chambre disponible au thurnage
    <i class="icon-remove"></i> Chambre non disponible au thurnage

    <br/><br/>
    <strong>Ces pages ont été crées pour rassembler dans un format
      plus pratique les différentes informations publiquement
      disponibles sur <a href="http://www.dg.ens.fr/thurnage/">le site
      de la DG</a>. Malgré tout le soin apporté au rassemblement de ces résultats, des erreurs et/ou omissions peuvent s'y être glissées et je ne garantie en aucun cas leur exactitude.
      </strong>

      <br />

      En particulier, l'état indiqué des thurnes, ainsi que la
      présence de Mezzanine, se base sur
      les <a href="http://www.dg.ens.fr/thurnage/EtatChambre.html">commentaires</a>
      des 4 dernières années, mais ne tiens pas compte d'éventuels
      travaux s'il n'y a pas eu de commentaire depuis - souvenez-vous
      en si vous regardez les chambres en Rataud, notamment. Vous
      pouvez lire les commentaires complets (avec la date) en
      survolant la chambre avec votre souris.

    <br /> Le classement est une indication de la popularité de la
    thurne calculé à partir du classement des personnes ayant choisi
    cette thurne au TG depuis 2007.

      <br />

      Merci à Abel Lacabanne pour avoir importé le plan des chambres
      d'Ulm et Jourdan, et merci à Guillaume Bury pour son script
      calculant le rang moyen des thurnes.

    <div style="height: 5px;"></div>

    {0}

    <div style="height: 200px;"></div>

    <!-- Scripts at end of page for faster loading -->
    <script src="lib/jquery/jquery-2.1.1.min.js"></script>
    <script src="lib/bootstrap/js/bootstrap.js"></script>
    <script type="text/javascript">
      $(document).ready(function()
      {
      $('[rel=popover]').popover({'placement': 'bottom'});
      });
</script>
  </body>
</html>
