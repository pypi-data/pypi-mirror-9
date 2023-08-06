Introdução
==========

Em alguns momentos enquanto estamos desenvolvendo sites ou memos sistemas, precisamos lidar com conjuntos de icones,
em especifico em sistemas web, temos um problema provocado pelo alto numero de requisições para buscar imagens. Uma técnica
bem difundida é a criação de espiritos de imagens.

Este trabalho pode ser um pouco complicado uma vez que envolve a manipulação de uma imagem onde teremos todos os icones
ali dispostos seguindo uma ordem e uma folha de estilo descrevendo como chegar a esta imagem. Este problema é até simples
quando temos somente um tipo de dimissão de imagens.

Para solucionar este problema é que esta ferramenta foi desenvolvida. Agora só precisamos colocar estas imagens em um diretório
e a ferramenta processa este diretório e gera o arquivo CSS, a Imagem e um arquivo HTML para que você possa se guiar no momento
da utilização dos icones.

Instalação
==========

A instalação da ferramenta se dá atraves do easy_install o mesmo pip, logo abaixo como seria o comando para sua instalação:

 | easy_install spritify

Ou

 | pip spritify

Os fontes podem ser baixando pelo mercurial oficial do projeto:

 | hg clone ssh://hg@bitbucket.org/rodrigopmatias/spritify

A ferramenta depende da PIL com suporte a manipulação a PNG, JPEG e GIF além da PIL ainda temos a dependencia da jinja2 mas esta já vai
ser instalada sem mais problemas.

Como usar
=========

Esta ferramenta foi desenvolvida para ser utilizada na linha de comando, mas pode ser facilmente utilizada como parte de alguma aplicação de deploy inclusive com o fabric.

Para saber das opções do spritify execute o seguinte comando em seu terminal:

 | usage: spritify.py [-h] [-v] [-p PATH] [-o OUTFILE] [-t TEMPLATE]
 |                     [-s SPIRITE_NAME]
 |
 | HTML Generator of thumb directory.
 |
 | optional arguments:
 |   -h, --help            show this help message and exit
 |   -v, --version         Print the version of generator.
 |   -p PATH, --path PATH  Path of base images to show in thum
 |   -o OUTFILE, --output OUTFILE
 |                         Path of file to out processed html with thumbs.
 |   -t TEMPLATE, --template TEMPLATE
 |                         HTML Template.
 |   -s SPIRITE_NAME, --spirite SPIRITE_NAME
 |                         Spirite name for css and HTML.

Se for passada **--path** for passado como parametro para a ferramenta ele irá tentar fazer  compilação para gerar os arquivos desejados. Mas caso seja passado o parametro **--version** a ferramenta irá somente mostrar as informações da verão do aplicativo.

O parametro **--path** indica ao aplicativo que ele deve fazer a geração do spirite, com está opção podemos utilizar outras para fugir pesonalizar a geração, veja logo abaixo:

1. Se utilizarmo o parametro **--output** iremos indicar o local onde queremos que seja gerado o arquivo HTML e os demais, se este for omitido será gerado no diretório pai do indicado como path e o nome do arquivo HTML será o nome do diretório indicado no path seguido da extenção .html.

2. Se utilizarmos o parametro **--template** poderemos indicar um arquivo de template para o HTML, caso queira personalizar uma template, fique livre para isto basta editar o arquivo `default.html`_ de template.

.. _default.html: https://bitbucket.org/rodrigopmatias/spritify/src/7986a0c5b6f4/templates/default.html

3. o parametro **--spirite** modifica o nome do spirite que será criado por padrão o nome do spirite seria o mesmo nome do arquivo indicado como output.

O resultado da execulção da ferramenta serão 3 arquivos:

1. SNIPTER.png, este arquivo contem todos as imagens que estávam presentes no diretório indicado como path, seguindo uma logica de colocação.

2. SNIPTER.css, um arquivo CSS que contem diretivas para encontrar cada imagem que estavam presentes no diretório indicado como path. Neste arquivo havera uma indicação **.icon-snipter** que se referenciará ao SNIPTER.png e depois para cada imagem uma diretiva **.icon-[SLUG DO NOME DO ARQUIVO DA IMAGEM]**.

3. SNIPTER.html, um arquivo para nos auxiliar a visualizar de forma organzada o conteúdo de SNIPTER.png, e ainda com informações das class CSS para poder utilziar aquela imagem em um código HTML.

Reportar problemas ou solicitando funcionalidades
=================================================

Para reportar algum problema, solicitar alguma funcionalidade basta acessar bitbucket_ e criar um novo issue.

.. _bitbucket: https://bitbucket.org/rodrigopmatias/spritify/issues/new

Contribuindo
============

Para contribuir com o projeto, você pode implementar uma funcionalidade que você acredita que seria util nesta ferramenta em um fork do nosso projeto, e quando a funcionalidade estiver estavel solicitar um pull que tão logo sua modificação será avaliada, você ainda pode pegar algum issue para ser implementado o processo se dá da mesma forma.