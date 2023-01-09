# Ensure these are absolute paths
from os.path import realpath, dirname, join

base_dir = realpath(dirname(__file__))
data_dir = realpath(join(base_dir, 'data'))

invoices_base_url = 'http://search.electoralcommission.org.uk/Api/Spending/Invoices/'
default_path_to_csv = data_dir + '/results.csv'
output_path = data_dir + '/v2/'
output_filetype = 'json'

labels = ['Transport', 'Miscellaneous', 'Catering', 'Accommodation', 'Expenses claimed by provider ', 'Completely unclear', 'Ambiguous and needs discussion ', 'ADVERTISING AND PRESS', 'Merchandise', 'Newspaper or magazine advertising', 'Radio advertising', 'Social media advertising', 'Online advertising (not social media,  i.e. web advertising but not online newspapers or social media)', 'Other forms of advertising (billboards, advans, digital posters outside)', 'PR', 'Campaign materials', 'Design services', 'Campaign material printing ', 'Direct Mail/ Leaflet delivery/ postage ', 'Infrastructure and equipment', 'Telecommunications services', 'Physical Security', 'Event costs/ Production/ Venue hire', 'Mobile application services', 'Email services', 'Website services', 'Search Engine Optimization', 'Recruitment services/staffing costs', 'Creative content owned by a third party (e.g. Getty images, PA images, demo music)', 'Translation/Braile/British Sign Language services', 'Campaign activity', 'GOTV', 'Fundraising ', 'Data and infrastructure', 'Campaign database or CRM (including SQL)', 'Data Services and analysis', 'IT infrastructure and support', 'Office supplies (staples, paperclips, IT equipment, envelopes)', 'Production Services ', 'Video editing/ production', 'Audio editing/production', 'Photos editing/production', 'Consultancy', 'Communication consultants', 'Design consultants', 'Ad strategy and consultancy', 'Social media strategy and consultancy', 'Data consultancy', 'Legal advice', 'Research', 'Polling', 'Focus groups', 'Ordinance survey data', 'Message testing', 'Archival research', 'Other forms of research', 'Social/Digital listening']