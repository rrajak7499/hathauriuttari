"""
Institutional Portal Configuration File.
Update the variables below to replicate and deploy this project for any school.
"""

SCHOOL_CONFIG = {
    # 1. School Identity & Contact Info
    "school_name": "Uchcha Madhyamic Vidyalaya Hathauri Uttari",
    "short_name": "U.M.V. Hathauri Uttari",
    "school_name_part_1": "Uchcha Madhyamic Vidyalaya",
    "school_name_part_2": "Hathauri Uttari",
    "board_affiliation": "BSEB Patna",
    "subdomain_slug": "hathauri-uttari",
    "address": "Uchcha Madhyamic Vidyalaya Hathauri Uttari, Kothra, Baheri, Darbhanga, Bihar - 847105",
    "primary_phone": "+91 9110962641",
    "email": "principal@umvhathauri.edu.in",
    "office_hours": "Monday – Saturday: 9:00 AM – 4:00 PM",
    "map_location_query": "Uchcha Madhyamic Vidyalaya Hathauri Uttari Baheri Darbhanga",
    "map_cordinates": "25.97133354435404, 85.9963287249768",
    "map_location_iframe": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3586.8889802702092!2d85.9957714461212!3d25.971681153567424!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x39edeb8e01b3e085%3A0x7af610d84988067c!2zR09WRVJOTUVOVCBTQ0hPT0wgS09USEFSQSAo4KS44KSw4KSV4KS-4KSw4KWAIOCkuOCljeCkleClguCksiDgpJXgpYvgpKDgpLDgpL4gKQ!5e0!3m2!1sen!2sin!4v1792214537484!5m2!1sen!2sin",

    # 2. Primary Portal Admin Account
    "admin_username": "principal_admin",
    "admin_email": "admin@umvhathauri.edu.in",
    "admin_password": "ChangeMe@2026",
    "admin_full_name": "Headmaster Office",

    # 3. Active Academic Session & Matrix
    "session_name": "2026-2027",
    "session_start": "2026-04-01",
    "session_end": "2027-03-31",
    # Automatically creates 9th, 10th, 11th, 12th with Science and Arts tracks
    "seed_standard_classes": True,

    "head_master_conatact_no_1": "+91-9110962641",
    "clerk_contact_no_1": "+91-7079192999",


    "headmaster": {
        "name": "Raman Jee Ray",
        "designation": "Headmaster",
        "qualifications": "M.Sc. (Physics), M.Ed, Ph.D.",
        "image_url": "https://i.postimg.cc/L5BS9BLw/hm.png",
        "experience": "7+ Years in Educational Administration",
        "email": "principal@umvhathauri.edu.in",
        "message_lead": "Guiding young minds through holistic education, academic discipline, and values.",
        "message_body": (
            "At Uchcha Madhyamic Vidyalaya Hathauri Uttari, we believe that true education "
            "transcends beyond the boundaries of textbooks. Our focus is to instill critical "
            "thinking, character, and national integrity in our students. We are steadfastly "
            "committed to providing an environment where every student discovers their latent "
            "potential and rises to meet the challenges of the future."
        ),
    },
    

    # 4. ImageKit / CDN Hero Banners
    "banners": [
        {
            "title": "Welcome to U.M.V Hathauri Uttari Academic Session 2026–27",
            "image_url": "https://images.unsplash.com/photo-1580582932707-520aed937b7b?auto=format&fit=crop&w=1600&q=80",
            "order": 1,
            "is_active": True,
        },
        {
            "title": "State-of-the-Art Science & Computer Laboratories",
            "image_url": "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=1600&q=80",
            "order": 2,
            "is_active": True,
        },
    ],

    # 5. Pre-seeded Notices (Uses Google Drive links)
    "notices": [
        {
            "title": "Commencement of New Academic Session 2026–27",
            "content": "All students from grades 9th to 12th are instructed to report in full uniform as classes commence as per the published timetable.",
            "priority": "important",
            "drive_link": "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/view?usp=sharing",
            "is_active": True,
        },
        {
            "title": "Urgent: BSEB Board Exam Registration Form Verification",
            "content": "Class 10 and 12 examinees must cross-check their subject declarations and admit details with their respective class teachers.",
            "priority": "urgent",
            "drive_link": "",
            "is_active": True,
        },
    ],

    # 6. Pre-seeded Downloadable Forms (Google Drive links)
    "downloads": [
        {
            "title": "Class 11th Admission Form & Eligibility Checklist",
            "category": "admission",
            "drive_link": "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/view?usp=sharing",
            "description": "Standard registration dossier for newly enrolled Science and Arts streams students.",
            "is_active": True,
        },
        {
            "title": "Transfer Certificate (TC) Application Form",
            "category": "administrative",
            "drive_link": "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/view?usp=sharing",
            "description": "Form for students requesting migration or school leaving certificates.",
            "is_active": True,
        },
        {
            "title": "Annual Examination Syllabus & Schedule",
            "category": "academic",
            "drive_link": "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/view?usp=sharing",
            "description": "Complete breakdown of terms, subjects, and grading guidelines.",
            "is_active": True,
        },
    ],
}