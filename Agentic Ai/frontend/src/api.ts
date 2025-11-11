export async function createProject(baseUrl: string, instruction: string) {
  const res = await fetch(`${baseUrl}/projects/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ instruction }),
  })
  if (!res.ok) {
    throw new Error(`Failed to create project: ${res.status}`)
  }
  return res.json()
}

export async function listProjects(baseUrl: string) {
  const res = await fetch(`${baseUrl}/projects/`, {
    method: 'GET'
  })
  if (!res.ok) throw new Error(`Failed to list projects: ${res.status}`)
  return res.json()
}


