import { API_ENDPOINTS } from './api';

export async function fetchPublications() {
  const res = await fetch(API_ENDPOINTS.publications);
  if (!res.ok) throw new Error('Erreur chargement publications');
  return res.json();
}

export async function fetchProjects() {
  const res = await fetch(API_ENDPOINTS.projects);
  if (!res.ok) throw new Error('Erreur chargement projets');
  return res.json();
}

export async function fetchDistinctions() {
  const res = await fetch(API_ENDPOINTS.distinctions);
  if (!res.ok) throw new Error('Erreur chargement distinctions');
  return res.json();
}

export async function fetchAcademicCareer() {
  const res = await fetch(API_ENDPOINTS.academic_career);
  if (!res.ok) throw new Error('Erreur chargement parcours académique');
  return res.json();
}

export async function switchLanguage(lang: string) {
  const res = await fetch(API_ENDPOINTS.lang(lang));
  if (!res.ok) throw new Error('Erreur changement langue');
  return res.json();
}