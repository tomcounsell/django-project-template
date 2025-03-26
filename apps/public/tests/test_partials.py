import os
from django.test import TestCase


class PartialsDirectoryTestCase(TestCase):
    """
    Tests for validating the partials directory structure and naming conventions
    """

    def test_partials_directory_exists(self):
        """Test that the partials directory exists in the templates directory"""
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'templates')
        partials_dir = os.path.join(templates_dir, 'partials')
        self.assertTrue(os.path.exists(partials_dir), "Partials directory does not exist")
        self.assertTrue(os.path.isdir(partials_dir), "Partials path is not a directory")

    def test_partials_directory_structure(self):
        """Test that the partials directory has appropriate subdirectories"""
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'templates')
        partials_dir = os.path.join(templates_dir, 'partials')
        
        # Define expected subdirectories for partials
        expected_subdirs = ['forms', 'lists', 'cards', 'modals', 'common']
        
        for subdir in expected_subdirs:
            subdir_path = os.path.join(partials_dir, subdir)
            self.assertTrue(os.path.exists(subdir_path), f"Partials subdirectory '{subdir}' does not exist")
            self.assertTrue(os.path.isdir(subdir_path), f"Partials path '{subdir}' is not a directory")

    def test_partial_base_template_exists(self):
        """Test that a base template for partials exists"""
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'templates')
        partial_base_path = os.path.join(templates_dir, 'partials', '_partial_base.html')
        
        self.assertTrue(os.path.exists(partial_base_path), "Partial base template does not exist")
        
        # Check content of the base partial template
        with open(partial_base_path, 'r') as f:
            content = f.read()
            
        # Verify that it has the required block(s)
        self.assertIn('{% block content %}', content, "Partial base template is missing content block")
        self.assertIn('{% endblock content %}', content, "Partial base template is missing endblock with name")
        
    def test_partial_naming_conventions(self):
        """Test that any partial templates follow the naming conventions"""
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'templates')
        partials_dir = os.path.join(templates_dir, 'partials')
        
        # Skip test if directory doesn't exist yet (will be caught by earlier test)
        if not os.path.exists(partials_dir):
            return
            
        # Walk through all subdirectories
        for root, dirs, files in os.walk(partials_dir):
            for file in files:
                if file.endswith('.html') and not file.startswith('_'):
                    # Check if the file name follows the convention of type_name.html
                    # e.g., "form_user.html", "card_team.html", etc.
                    parts = file.replace('.html', '').split('_')
                    self.assertTrue(len(parts) >= 2, 
                                    f"Partial template '{file}' should follow naming convention 'type_name.html'")
                    
                    # Check that the file is in the correct subdirectory
                    subdir_name = os.path.basename(root)
                    if subdir_name != 'common':
                        expected_prefix = subdir_name[:-1] if subdir_name.endswith('s') else subdir_name
                        self.assertEqual(parts[0], expected_prefix, 
                                        f"Partial in '{subdir_name}' should have prefix '{expected_prefix}_'")
        
    def test_partial_templates_extend_base(self):
        """Test that all partial templates extend the correct base template"""
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'templates')
        partials_dir = os.path.join(templates_dir, 'partials')
        
        # Skip test if directory doesn't exist yet (will be caught by earlier test)
        if not os.path.exists(partials_dir):
            return
            
        # Walk through all subdirectories
        for root, dirs, files in os.walk(partials_dir):
            for file in files:
                if file.endswith('.html') and not file.startswith('_'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Check if the file has an extends statement
                    extends_pattern = r'{%\s*extends\s+"([^"]+)"\s*%}'
                    import re
                    extends_match = re.search(extends_pattern, content)
                    
                    # Make sure it extends something
                    self.assertIsNotNone(extends_match, 
                                         f"Partial template '{file}' should extend a base template")
                    
                    # Get the template that it extends
                    extends_template = extends_match.group(1)
                    
                    # Check if it's in the modals directory
                    if os.path.basename(root) == 'modals':
                        # Modals can extend the modals base template
                        if not file.startswith('_'):  # Skip _modal_base.html
                            self.assertIn('modals/_modal_base.html', extends_template, 
                                         f"Modal template '{file}' should extend a modal base template")
                    else:
                        # Other partials should extend partial_base or base templates
                        acceptable_bases = ['partials/_partial_base.html', 'partial.html']
                        self.assertTrue(any(base in extends_template for base in acceptable_bases),
                                      f"Partial template '{file}' should extend one of: {acceptable_bases}")