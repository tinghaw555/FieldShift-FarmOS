'use client'

import { MapPin, Sprout, Satellite, Repeat, Sliders, Cpu, Target, Database } from 'lucide-react'

export default function Navigation() {
  const sections = [
    { id: 'farm', label: 'Farm Location', icon: MapPin },
    { id: 'planting-suitability', label: 'Check Planting', icon: Sprout },
    { id: 'earth-observation', label: 'Climate Data', icon: Satellite },
    { id: 'rotation-lab', label: 'Compare Plans', icon: Repeat },
    { id: 'flippoint', label: 'What If', icon: Sliders },
    { id: 'smart-farm', label: 'Monitoring', icon: Cpu },
    { id: 'ground-truth', label: 'Validation', icon: Target },
    { id: 'farm-data', label: 'My Data', icon: Database },
  ]

  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-charcoal-200 shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex items-center gap-1 overflow-x-auto py-2">
          {sections.map((section) => {
            const Icon = section.icon
            return (
              <a
                key={section.id}
                href={`#${section.id}`}
                className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium
                         text-charcoal-700 hover:bg-forest-50 hover:text-forest-700
                         transition-colors whitespace-nowrap"
              >
                <Icon className="w-4 h-4" />
                {section.label}
              </a>
            )
          })}
        </div>
      </div>
    </nav>
  )
}
