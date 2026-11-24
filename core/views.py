from django.shortcuts import render, redirect
from django.contrib import messages
from .models import BlogPost, ContactMessage
from .forms import ContactForm


def landing_page(request):
    # Fetch 3 blog posts for Insights section
    insights = BlogPost.objects.filter(is_published=True)[:3]
    
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            contact_form.save()
            messages.success(request, "Thank you for reaching out! Your message has been sent to our placement office.")
            return redirect('/#contact')
        else:
            messages.error(request, "Please check the contact form fields and try again.")
    else:
        contact_form = ContactForm()

    context = {
        'insights': insights,
        'contact_form': contact_form,
    }
    return render(request, 'landing/index.html', context)
