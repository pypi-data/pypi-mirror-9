from cStringIO import StringIO

from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status, viewsets, generics, renderers
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse

from po_projects.models import Project, ProjectVersion
from po_projects.rest.serializers import ProjectCurrentSerializer, ProjectVersionSerializer
from po_projects.mixins import DownloadMixin
from po_projects.dump import po_project_export

@api_view(('GET',))
def api_root(request, format=None):
    """
    This is the entry point that display available endpoints for this API
    """
    return Response({
        'projects': reverse('po_projects:api-project-list', request=request, format=format)
    })


class ProjectList(APIView):
    """
    List all available projects
    """
    def get(self, request, format=None):
        projects = Project.objects.all()
        serializer = ProjectCurrentSerializer(projects, many=True, context={'request': request})

        return Response(serializer.data)


class ProjectDetailMixin(object):
    """
    Mixin to get Project object
    
    NOTE: is this required anymore ?
    """
    def get_object(self):
        return get_object_or_404(Project, slug=self.kwargs['slug'])


class ProjectCurrentDetail(ProjectDetailMixin, generics.RetrieveUpdateAPIView):
    """
    Retrieve and update the current last version of a project instance from its slug. 
    
    * ``projectversion_set`` attribute will contains the project versions;
    * ``tarball_url`` attribute is a link to download a ZIP archive of PO files for the 
      current project version.
    
    ``projectversion_set`` urls use the version ID (pk), not the slug or version name.
    
    This view is a "Retrieve and update" view, so you can see and get project details 
    but also update its content.
    
    The ``pot`` field is optionnal, you can fill it with the content of a valid POT file 
    to update project template catalog and its translation catalogs.
    """
    serializer_class = ProjectCurrentSerializer
    model = Project


class ProjectVersionDetail(APIView):
    """
    Retrieve a project instance for a specific version given by its ID.
    
    Project versions are freezed, so you can't update them.
    """
    def get_object(self, pk):
        return get_object_or_404(ProjectVersion, pk=pk)

    def get(self, request, pk, format=None):
        self.project_version = self.get_object(pk)
        self.object = self.project_version.project
        serializer = ProjectVersionSerializer(self.object, context={'request': request})
        return Response(serializer.data)


class ProjectArchive(ProjectDetailMixin, DownloadMixin, APIView):
    """
    Send a ZIP archive for the project's PO files
    """
    content_type = 'application/x-gzip'
    filename_format = "{project_slug}_{timestamp}.tar.gz"
    
    def get(self, request, slug, format=None):
        self.object = self.get_object()
        return super(ProjectArchive, self).get(request)

    def get_context_data(self, **kwargs):
        context = super(ProjectArchive, self).get_context_data(**kwargs)
        context.update({
            'project': self.object,
            'project_slug': self.object.slug,
            'timestamp': self.get_filename_timestamp(),
        })
        return context
    
    def get_filename(self, context):
        return self.filename_format.format(**context)
    
    def get_content(self, context):
        archive_file = StringIO()
        
        po_project_export(self.object, self.object.get_current_version(), archive_file)
        
        return archive_file.getvalue()
