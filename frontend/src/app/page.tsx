'use client'

import { useState } from 'react'
import StatusBar from '@/components/StatusBar'
import Navigation from '@/components/Navigation'
import FarmSection from '@/components/sections/FarmSection'
import PlantingSuitabilitySection from '@/components/sections/PlantingSuitabilitySection'
import EarthObservationSection from '@/components/sections/EarthObservationSection'
import RotationLabSection from '@/components/sections/RotationLabSection'
import FlipPointSection from '@/components/sections/FlipPointSection'
import SmartFarmSection from '@/components/sections/SmartFarmSection'
import GroundTruthSection from '@/components/sections/GroundTruthSection'
import FarmDataSection from '@/components/sections/FarmDataSection'

export default function Dashboard() {
  const [selectedFarm, setSelectedFarm] = useState<any>(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const handleFarmSelected = (farm: any) => {
    setSelectedFarm(farm)
    setRefreshTrigger(prev => prev + 1)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-charcoal-50 to-forest-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-forest-800 to-forest-700 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">FieldShift FarmOS</h1>
              <p className="text-forest-100 text-sm mt-1">
                Observe Earth. Predict Risks. Improve Decisions. Verify Reality.
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Status Bar */}
      <StatusBar farm={selectedFarm} />

      {/* Navigation */}
      <Navigation />

      {/* Main Dashboard - Single Page */}
      <main className="container mx-auto px-4 py-6 space-y-8">
        
        {/* Section 1: Farm Location */}
        <section id="farm" className="scroll-mt-20">
          <FarmSection onFarmSelected={handleFarmSelected} selectedFarm={selectedFarm} />
        </section>

        {/* Section 2: Check Planting Suitability - PRIMARY WORKFLOW */}
        <section id="planting-suitability" className="scroll-mt-20">
          <PlantingSuitabilitySection farm={selectedFarm} />
        </section>

        {/* Section 3: Earth Observation & Weather */}
        <section id="earth-observation" className="scroll-mt-20">
          <EarthObservationSection farm={selectedFarm} refreshTrigger={refreshTrigger} />
        </section>

        {/* Section 4: Crop Rotation Comparison */}
        <section id="rotation-lab" className="scroll-mt-20">
          <RotationLabSection farm={selectedFarm} />
        </section>

        {/* Section 5: FlipPoint & Agricultural Risk */}
        <section id="flippoint" className="scroll-mt-20">
          <FlipPointSection farm={selectedFarm} />
        </section>

        {/* Section 6: Smart Farm & Irrigation */}
        <section id="smart-farm" className="scroll-mt-20">
          <SmartFarmSection farm={selectedFarm} />
        </section>

        {/* Section 7: Ground Truth & Evidence */}
        <section id="ground-truth" className="scroll-mt-20">
          <GroundTruthSection farm={selectedFarm} />
        </section>

        {/* Section 8: My Farm Data & Analysis (Phase 2) */}
        <section id="farm-data" className="scroll-mt-20">
          <FarmDataSection farm={selectedFarm} />
        </section>

        {/* Data Sources & Methodology - Collapsed by Default */}
        <section className="scroll-mt-20">
          <details className="bg-white rounded-lg shadow-lg overflow-hidden">
            <summary className="cursor-pointer p-6 hover:bg-charcoal-50 transition-colors">
              <h2 className="text-2xl font-bold text-charcoal-900 inline-flex items-center gap-2">
                📊 Data Sources & Methodology
              </h2>
              <p className="text-charcoal-600 mt-1 text-sm">
                Technical details about data providers, models, assumptions, and limitations
              </p>
            </summary>
            
            <div className="p-6 border-t border-charcoal-200 space-y-6">
              {/* Data Sources */}
              <div>
                <h3 className="font-semibold text-charcoal-900 mb-3 text-lg">Available Data Sources</h3>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                      <span className="font-semibold">NASA POWER</span>
                    </div>
                    <p className="text-charcoal-700">Historical climate data (1981-present). Global coverage at ~50km resolution. Provides temperature, precipitation, solar radiation, humidity, and wind speed.</p>
                  </div>
                  <div className="p-3 bg-sky-50 rounded-lg border border-sky-200">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                      <span className="font-semibold">Open-Meteo</span>
                    </div>
                    <p className="text-charcoal-700">7-day weather forecasts. Accuracy decreases beyond 3 days. CC BY 4.0 license.</p>
                  </div>
                  <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-200">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                      <span className="font-semibold">FAO-56</span>
                    </div>
                    <p className="text-charcoal-700">Crop coefficient method for calculating evapotranspiration. Peer-reviewed, established science from FAO Irrigation & Drainage Paper 56 (Allen et al. 1998).</p>
                  </div>
                  <div className="p-3 bg-amber-50 rounded-lg border border-amber-200">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
                      <span className="font-semibold">ERA5-Land / Sentinel-2</span>
                    </div>
                    <p className="text-charcoal-700">Optional satellite data sources (not yet integrated).</p>
                  </div>
                </div>
              </div>

              {/* Model Assumptions */}
              <div>
                <h3 className="font-semibold text-charcoal-900 mb-3 text-lg">Model Assumptions</h3>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div className="p-3 bg-charcoal-50 rounded-lg border border-charcoal-200">
                    <div className="font-semibold text-charcoal-900 mb-2">Water Balance Model</div>
                    <ul className="space-y-1 text-charcoal-700">
                      <li>• Effective rainfall: 80%</li>
                      <li>• Climate year: 2023 historical data</li>
                      <li>• Method: Simplified FAO-56 crop coefficients</li>
                      <li>• ET0 calculation: Temperature-based approximation</li>
                    </ul>
                  </div>
                  <div className="p-3 bg-charcoal-50 rounded-lg border border-charcoal-200">
                    <div className="font-semibold text-charcoal-900 mb-2">Crop Parameters</div>
                    <ul className="space-y-1 text-charcoal-700">
                      <li>• Uses average Kc values (not growth-stage specific)</li>
                      <li>• Standard crop coefficients from FAO-56</li>
                      <li>• No soil moisture tracking in simplified version</li>
                      <li>• Generic soil parameters (can be customized)</li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Data Limitations */}
              <div>
                <h3 className="font-semibold text-charcoal-900 mb-3 text-lg">Data Limitations</h3>
                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-sm">
                  <ul className="space-y-2 text-charcoal-700">
                    <li>• <strong>NASA POWER:</strong> ~50km gridded estimates, not point measurements. Local conditions may vary significantly.</li>
                    <li>• <strong>Weather Forecasts:</strong> Accuracy decreases beyond 3 days. Use for short-term planning only.</li>
                    <li>• <strong>Crop Models:</strong> Simplified calculations for comparison, not precision agriculture. Values are estimates.</li>
                    <li>• <strong>No Site Calibration:</strong> Generic parameters used. Local soil, variety, and management differ.</li>
                    <li>• <strong>Historical Data Only:</strong> Uses 2023 climate. Future years will differ due to climate variability.</li>
                  </ul>
                </div>
              </div>

              {/* Scientific Transparency */}
              <div>
                <h3 className="font-semibold text-charcoal-900 mb-3 text-lg">Scientific Transparency</h3>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                    <div className="font-semibold text-charcoal-900 mb-2">What This Tool Does Well</div>
                    <ul className="space-y-1 text-charcoal-700">
                      <li>• FAO-56 is peer-reviewed, established science</li>
                      <li>• Water balance math is internally consistent</li>
                      <li>• Model assumptions are documented</li>
                      <li>• Code is unit-tested and transparent</li>
                      <li>• Provides <em>comparative</em> analysis of rotation strategies</li>
                    </ul>
                  </div>
                  <div className="p-3 bg-red-50 rounded-lg border border-red-200">
                    <div className="font-semibold text-charcoal-900 mb-2">What This Tool Cannot Do</div>
                    <ul className="space-y-1 text-charcoal-700">
                      <li>• Predict absolute yields</li>
                      <li>• Replace local agronomic expertise</li>
                      <li>• Account for pests, diseases, or market prices</li>
                      <li>• Guarantee field performance</li>
                      <li>• Substitute for local measurements and calibration</li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Evidence & Validation */}
              <div>
                <h3 className="font-semibold text-charcoal-900 mb-3 text-lg">Evidence Inspector</h3>
                <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg text-sm">
                  <div className="grid md:grid-cols-3 gap-4 mb-4">
                    <div>
                      <div className="font-semibold text-charcoal-900 mb-1">Ground Truth</div>
                      <p className="text-charcoal-700">Upload field observations (photos, notes, sensor data) to compare predictions with reality.</p>
                    </div>
                    <div>
                      <div className="font-semibold text-charcoal-900 mb-1">Validation Status</div>
                      <p className="text-charcoal-700">Core calculations unit-tested. Field validation in progress. Not yet validated against real farm outcomes.</p>
                    </div>
                    <div>
                      <div className="font-semibold text-charcoal-900 mb-1">Simulation Mode</div>
                      <p className="text-charcoal-700">ESP32 sensor data is currently simulated for demo purposes. Real hardware integration planned.</p>
                    </div>
                  </div>
                  <div className="p-3 bg-white rounded-lg border border-purple-300">
                    <strong>Bottom Line:</strong> FieldShift provides scientifically defensible <em>comparisons</em> between rotation strategies using established methods. It cannot predict absolute yields or guarantee field performance without local calibration. Start with small trials, collect data, and refine decisions iteratively.
                  </div>
                </div>
              </div>

              {/* FlipPoint Methodology */}
              <div>
                <h3 className="font-semibold text-charcoal-900 mb-3 text-lg">How FlipPoint Works</h3>
                <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg text-sm text-charcoal-700">
                  <p>FlipPoint re-runs the actual water balance model at each parameter value. The threshold where the preferred rotation changes is the "flip point." This is not a statistical prediction—it shows how your decision depends on assumptions you can verify or improve with better data.</p>
                </div>
              </div>

              {/* Documentation Links */}
              <div>
                <h3 className="font-semibold text-charcoal-900 mb-3 text-lg">Documentation</h3>
                <div className="grid md:grid-cols-3 gap-3 text-sm">
                  <div className="p-3 bg-charcoal-50 rounded-lg border border-charcoal-200">
                    <div className="font-semibold text-charcoal-900">MODEL_LIMITATIONS.md</div>
                    <p className="text-charcoal-600 text-xs mt-1">Detailed model constraints and assumptions</p>
                  </div>
                  <div className="p-3 bg-charcoal-50 rounded-lg border border-charcoal-200">
                    <div className="font-semibold text-charcoal-900">VALIDATION.md</div>
                    <p className="text-charcoal-600 text-xs mt-1">Validation status and testing results</p>
                  </div>
                  <div className="p-3 bg-charcoal-50 rounded-lg border border-charcoal-200">
                    <div className="font-semibold text-charcoal-900">AI_DISCLOSURE.md</div>
                    <p className="text-charcoal-600 text-xs mt-1">AI assistance disclosure</p>
                  </div>
                </div>
              </div>
            </div>
          </details>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-charcoal-900 text-charcoal-300 mt-12 py-8">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-white font-semibold mb-2">Data Sources</h3>
              <ul className="text-sm space-y-1">
                <li>NASA POWER (Climate Data)</li>
                <li>Open-Meteo (Weather Forecasts)</li>
                <li>FAO-56 (Crop Coefficients)</li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-2">Documentation</h3>
              <ul className="text-sm space-y-1">
                <li>Model Limitations</li>
                <li>Validation Status</li>
                <li>AI Disclosure</li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-2">Status</h3>
              <ul className="text-sm space-y-1">
                <li>Phase: P0A Core Foundation</li>
                <li>ESP32: Software Simulation</li>
                <li>Version: 1.0.0</li>
              </ul>
            </div>
          </div>
          <div className="mt-6 pt-6 border-t border-charcoal-700 text-center text-sm">
            <p>FieldShift FarmOS © 2026 | MIT License</p>
            <p className="text-xs mt-1 text-charcoal-400">
              This tool provides decision support only. Not a substitute for professional agronomic advice.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
