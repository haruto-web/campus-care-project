# Campus Care UI Design System

## Design Principles

All HTML templates in Campus Care follow a consistent, modern design system using Tailwind CSS.

---

## Layout Structure

### Page Container
```html
<div class="max-w-7xl mx-auto px-4 py-6">
  <!-- Content -->
</div>
```

### Page Header
```html
<div class="flex justify-between items-center mb-6">
    <div>
        <h2 class="text-3xl font-bold text-gray-800">Page Title</h2>
        <p class="text-gray-600 mt-1">Subtitle or description</p>
    </div>
    <a href="{% url 'back_url' %}" class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition">
        <i class="bi bi-arrow-left"></i> Back
    </a>
</div>
```

---

## Cards & Containers

### White Card with Shadow
```html
<div class="bg-white rounded-lg shadow-lg">
    <div class="p-8">
        <!-- Content -->
    </div>
</div>
```

### Card with Colored Header
```html
<div class="bg-white rounded-lg shadow">
    <div class="bg-blue-600 text-white px-6 py-4 rounded-t-lg">
        <h5 class="text-lg font-semibold">Section Title</h5>
    </div>
    <div class="p-6">
        <!-- Content -->
    </div>
</div>
```

---

## Forms

### Form Input
```html
<div class="mb-6">
    <label for="field_id" class="block text-sm font-semibold text-gray-700 mb-2">
        Field Label <span class="text-red-500">*</span>
    </label>
    <input type="text" 
           id="field_id" 
           name="field_name"
           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
           placeholder="Placeholder text..."
           required>
</div>
```

### Textarea
```html
<textarea 
    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
    rows="4"
    placeholder="Enter text..."></textarea>
```

### Select Dropdown
```html
<select class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition">
    <option value="">Choose option...</option>
    <option value="1">Option 1</option>
</select>
```

### Form Buttons (Two Column)
```html
<div class="flex gap-3">
    <button type="submit" class="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition font-semibold">
        <i class="bi bi-check-circle"></i> Submit
    </button>
    <a href="{% url 'cancel_url' %}" class="flex-1 bg-gray-200 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-300 transition font-semibold text-center">
        Cancel
    </a>
</div>
```

---

## Buttons

### Primary Button
```html
<button class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition font-semibold">
    <i class="bi bi-icon"></i> Button Text
</button>
```

### Secondary Button
```html
<button class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition">
    Button Text
</button>
```

### Success Button
```html
<button class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition">
    <i class="bi bi-check"></i> Success
</button>
```

### Danger Button
```html
<button class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition">
    <i class="bi bi-trash"></i> Delete
</button>
```

### Text Link Button
```html
<a href="#" class="text-blue-600 hover:text-blue-800">
    <i class="bi bi-icon"></i> Link Text
</a>
```

---

## Tables

### Standard Table
```html
<div class="bg-white rounded-lg shadow overflow-hidden">
    <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
            <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Column</th>
            </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 text-sm text-gray-900">Data</td>
            </tr>
        </tbody>
    </table>
</div>
```

---

## Lists & Cards

### Grid Layout
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <div class="bg-white rounded-lg shadow p-6">
        <!-- Card content -->
    </div>
</div>
```

### Vertical List
```html
<div class="space-y-3">
    <div class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition">
        <!-- List item -->
    </div>
</div>
```

---

## Alerts & Messages

### Info Alert
```html
<div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-lg">
    <p class="text-blue-700">
        <i class="bi bi-info-circle"></i> Information message
    </p>
</div>
```

### Success Alert
```html
<div class="bg-green-50 border-l-4 border-green-500 p-4 rounded-lg">
    <p class="text-green-700">Success message</p>
</div>
```

### Warning Alert
```html
<div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-lg">
    <p class="text-yellow-700">Warning message</p>
</div>
```

### Error Alert
```html
<div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
    <p class="text-red-700">Error message</p>
</div>
```

---

## Badges

### Status Badges
```html
<!-- High Risk -->
<span class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">High</span>

<!-- Medium Risk -->
<span class="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">Medium</span>

<!-- Low Risk -->
<span class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Low</span>

<!-- Info -->
<span class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">Info</span>
```

---

## Color Palette

### Primary Colors
- **Blue**: `bg-blue-600`, `text-blue-600`, `hover:bg-blue-700`
- **Gray**: `bg-gray-600`, `text-gray-600`, `hover:bg-gray-700`

### Status Colors
- **Success/Green**: `bg-green-600`, `text-green-600`
- **Warning/Yellow**: `bg-yellow-500`, `text-yellow-500`
- **Danger/Red**: `bg-red-600`, `text-red-600`
- **Info/Blue**: `bg-blue-500`, `text-blue-500`

### Text Colors
- **Primary**: `text-gray-800` (headings)
- **Secondary**: `text-gray-600` (body text)
- **Muted**: `text-gray-500` (helper text)

---

## Typography

### Headings
```html
<h1 class="text-4xl font-bold text-gray-800">H1 Heading</h1>
<h2 class="text-3xl font-bold text-gray-800">H2 Heading</h2>
<h3 class="text-2xl font-bold text-gray-800">H3 Heading</h3>
<h4 class="text-xl font-semibold text-gray-800">H4 Heading</h4>
<h5 class="text-lg font-semibold text-gray-800">H5 Heading</h5>
```

### Body Text
```html
<p class="text-gray-700">Regular paragraph text</p>
<p class="text-gray-600">Secondary text</p>
<small class="text-gray-500">Helper or muted text</small>
```

---

## Spacing

### Margins
- `mb-6`: Bottom margin for sections
- `mb-4`: Bottom margin for form fields
- `mb-3`: Bottom margin for smaller elements
- `mt-1`: Small top margin for subtitles

### Padding
- `p-8`: Large padding for main cards
- `p-6`: Medium padding for sections
- `p-4`: Small padding for list items
- `px-4 py-3`: Input field padding
- `px-6 py-3`: Button padding

---

## Responsive Design

### Breakpoints
- `md:` - Medium screens (768px+)
- `lg:` - Large screens (1024px+)

### Grid Responsive
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
```

---

## Icons

Using Bootstrap Icons:
```html
<i class="bi bi-icon-name"></i>
```

Common icons:
- `bi-check-circle` - Success/Complete
- `bi-x-circle` - Error/Cancel
- `bi-info-circle` - Information
- `bi-arrow-left` - Back navigation
- `bi-plus-circle` - Add/Create
- `bi-trash` - Delete
- `bi-pencil` - Edit
- `bi-eye` - View
- `bi-upload` - Upload
- `bi-download` - Download

---

## Transitions

All interactive elements should have smooth transitions:
```html
class="transition hover:bg-blue-700"
```

---

## Summary

**Key Principles:**
1. Use Tailwind CSS classes exclusively
2. Consistent spacing (p-8 for cards, mb-6 for sections)
3. Large, comfortable input fields (py-3)
4. Semibold labels with red asterisks for required fields
5. Two-column button layout (Submit + Cancel)
6. Shadow cards with rounded corners
7. Hover effects on all interactive elements
8. Blue as primary color, gray for secondary
9. Responsive grid layouts
10. Clean, minimal design with good whitespace
