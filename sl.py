#!/usr/bin/env python

import json
import markdown
import optparse
import glob
import os
import sys
import re
import jinja2
import shutil
import feedgenerator

# Get me my config values!
def read_config(input_dir):
  config_location = input_dir + '/config.json'
  if os.path.isfile(config_location):
    with open(config_location) as config_file:    
      config = json.load(config_file)
    return config
  else:
    print 'config file %s is missing' % config_location
    sys.exit()

# What am I trying to translate?
def read_body(entry_file):
  mdfile = open(entry_file).read()
  html = markdown.markdown(mdfile)
  return html

# Where is the stuff?
def get_input_dir():
  parser = optparse.OptionParser()
  parser.add_option('-i', action="store", help="Where are your input files located?", dest="input_dir", default="./")
  (options, args) = parser.parse_args()
  return options.input_dir

# Create metadata from the markdown filename
def get_meta_data(base_filename):
  path,filename = os.path.split(base_filename)
  filename_split = re.split('-', filename)
  return filename_split

# Get series
def get_series(metadata):
  series = metadata[0]
  return series

# Get episode info
def get_epinfo(metadata):
  epinfo = metadata[1]
  return epinfo

# Make the title
def get_title(metadata):
  title = ' '.join(metadata[2:])
  return title

# Given the jinja for header or footer, render it to html
def render_jinja(incoming_template,metadata,config):
  epinfo = get_epinfo(metadata)
  title = get_title(metadata).title()
  blog_name = config['blog_name']
  meta_keywords = config['meta_keywords']
  meta_description = config['meta_description']
  language = config['language']
  author = config['author']
  base_url = config['base_url']
  url_location = config['url_location']
  template = jinja2.Template(incoming_template)
  rendered_jinja = template.render(
    title=title,
    epinfo=epinfo,
    blog_name=blog_name,
    meta_keywords=meta_keywords,
    meta_description=meta_description,
    language=language,
    base_url=base_url,
    url_location=url_location,
    author=author
  )
  return rendered_jinja

# Copy the style sheet into place
def copy_style(config):
  css_file = config['css_file'] 
  path,filename = os.path.split(css_file)
  dest_file = config['output'] + '/' + filename
  shutil.copyfile(css_file,dest_file)

# Create dir
def make_dir(dir):
  try:
    os.stat(dir)
  except:
    os.mkdir(dir)
    
# Get completed entry files
def get_completed_entries(input_dir):
  return sorted(glob.glob(input_dir + '/*/*.md'), reverse=False)
    
# Do the doing
def process_entries(input_dir,config):
  header_template = open(config['header_file']).read()
  footer_template = open(config['footer_file']).read()
  entry_files = glob.glob(input_dir + '/*.md')
  for entry_file in entry_files:
    base_filename = os.path.splitext(entry_file)[0]
    metadata = get_meta_data(base_filename)
    series = get_series(metadata)
    processed_dir = '%s/%s' % (input_dir,series)
    output_dir = '%s/%s' % (config['output'],series)
    path,filename = os.path.split(base_filename)
    make_dir(processed_dir)
    make_dir(output_dir)
    html_filename = '%s/%s.html' % (output_dir,filename)
    header_html = render_jinja(header_template,metadata,config)
    footer_html = render_jinja(footer_template,metadata,config)
    body_html = read_body(entry_file)
    html_doc = header_html + body_html + footer_html
    blog_file = open(html_filename,'w')
    blog_file.write(html_doc)
    blog_file.close()
    if os.path.isfile(html_filename):
      shutil.move(entry_file,processed_dir)
      print '%s has been processed.' % entry_file

# Let people find their way around
def create_archive_page(input_dir,config):
  index_filename = config['output'] + '/index.html'
  author = config['author']
  metadata = ['','','',author]
  output_dir = config['output']
  prev_series = -1
  header_template = open(config['header_file']).read()
  footer_template = open(config['footer_file']).read()
  header_html = render_jinja(header_template,metadata,config)
  footer_html = render_jinja(footer_template,metadata,config)
  entry_files = get_completed_entries(input_dir)
  index_filecontents = '%s' % header_html 
  for entry_file in entry_files:
    base_filename = os.path.splitext(entry_file)[0]
    metadata = get_meta_data(base_filename)
    path,filename = os.path.split(base_filename)
    title = get_title(metadata).title()
    epinfo = get_epinfo(metadata)
    cur_series = get_series(metadata)
    html_filename = '%s/%s.html' % (cur_series,filename)
    if cur_series != prev_series:
      index_filecontents = '%s <h1>%s</h1>' % (index_filecontents,cur_series)
      prev_series = cur_series
    index_filecontents = '%s <a href="%s">%s</a> (%s) <br />' % (index_filecontents,html_filename,title,epinfo)
  index_filecontents = index_filecontents + footer_html
  index_file = open(index_filename,'w')
  index_file.write(index_filecontents)
  index_file.close()

# Generator those fancy rss feeds
def create_rss_feed(input_dir,config):
  counter = 0
  rss_filename = config['output'] + '/feed.rss'
  blog_name = config['blog_name']
  author = config['author']
  language = config['language']
  url = config['base_url'] + config['url_location']
  meta_description = config['meta_description']
  feed_entries = int(config['feed_entries'])
  feed = feedgenerator.Rss201rev2Feed(
    title=blog_name,
    link=url,
    description=meta_description,
    language=language,
    feed_guid=url,
    feed_url='%sfeed.rss' % url
  )
  entry_files = get_completed_entries(input_dir)
  for entry_file in entry_files:
    counter = counter + 1
    if counter > feed_entries:
      break
    else:
      base_filename = os.path.splitext(entry_file)[0]
      metadata = get_meta_data(base_filename)
      path,filename = os.path.split(base_filename)
      html_filename = filename + '.html'
      epinfo = get_epinfo(metadata)
      series = get_series(metadata)
      title = get_title(metadata).title()
      feed.add_item(
        title=title,
        link='%s%s/%s' % (url,series,html_filename),
        description=title,
        author_name=author,
        unique_id='%s%s/%s' % (url,series,html_filename),
        unique_id_is_permalink="true"
      )

  with open(rss_filename, 'w') as rss_file:
    feed.write(rss_file, 'utf-8')

# Go Speed Go
def run():
  input_dir = get_input_dir()
  config = read_config(input_dir)
  copy_style(config)
  process_entries(input_dir,config)
  create_archive_page(input_dir,config)
  create_rss_feed(input_dir,config)

# Make it so!
run()
