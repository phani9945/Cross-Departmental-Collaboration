import { useEffect, useState } from 'react'
import { createProject, listProjects } from './api'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function App() {
  const [instruction, setInstruction] = useState('')
  const [projects, setProjects] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function refresh() {
    try {
      setError(null)
      const data = await listProjects(API_BASE)
      setProjects(data)
    } catch (e: any) {
      setError(e.message)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  async function onCreate(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      await createProject(API_BASE, instruction)
      setInstruction('')
      await refresh()
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto p-6 space-y-8">
        <h1 className="text-2xl font-semibold">Agentic AI Collaboration Platform</h1>
        <form onSubmit={onCreate} className="bg-white rounded border p-4 space-y-3">
          <label className="block text-sm font-medium">Project Instruction</label>
          <textarea
            className="w-full border rounded p-2"
            rows={4}
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            placeholder="Describe the interdisciplinary program you want to create..."
          />
          <button
            type="submit"
            disabled={loading || !instruction.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
          >
            {loading ? 'Creating...' : 'Create Project'}
          </button>
          {error && <div className="text-red-600 text-sm">{error}</div>}
        </form>
        <div className="space-y-2">
          <h2 className="text-xl font-semibold">Projects</h2>
          <div className="grid gap-3">
            {projects.map((p) => (
              <div key={p.id} className="bg-white rounded border p-3">
                <div className="font-medium">{p.title}</div>
                <div className="text-sm text-gray-600">{p.summary}</div>
                {p.crew_jobs?.length > 0 && (
                  <div className="text-xs text-gray-500 mt-1">
                    Crew Job: {p.crew_jobs[0].external_id} ({p.crew_jobs[0].status})
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}


