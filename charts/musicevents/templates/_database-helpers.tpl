{{/* Database URL parsing helpers */}}
{{- define "musicevents.database.user" -}}
{{- $parts := regexSplit "://" .Values.databaseUrl 2 }}
{{- if eq (len $parts) 2 }}
  {{- $credentials := regexSplit "@" (index $parts 1) 2 }}
  {{- if eq (len $credentials) 2 }}
    {{- $userpass := regexSplit ":" (index $credentials 0) 2 }}
    {{- if eq (len $userpass) 2 }}
      {{- index $userpass 0 }}
    {{- else }}
      {{- "musicevents" }}
    {{- end }}
  {{- else }}
    {{- "musicevents" }}
  {{- end }}
{{- else }}
  {{- "musicevents" }}
{{- end }}
{{- end -}}

{{- define "musicevents.database.password" -}}
{{- $parts := regexSplit "://" .Values.databaseUrl 2 }}
{{- if eq (len $parts) 2 }}
  {{- $credentials := regexSplit "@" (index $parts 1) 2 }}
  {{- if eq (len $credentials) 2 }}
    {{- $userpass := regexSplit ":" (index $credentials 0) 2 }}
    {{- if eq (len $userpass) 2 }}
      {{- index $userpass 1 }}
    {{- else }}
      {{- "musicevents" }}
    {{- end }}
  {{- else }}
    {{- "musicevents" }}
  {{- end }}
{{- else }}
  {{- "musicevents" }}
{{- end }}
{{- end -}}

{{- define "musicevents.database.name" -}}
{{- $parts := regexSplit "://" .Values.databaseUrl 2 }}
{{- if eq (len $parts) 2 }}
  {{- $credentials := regexSplit "@" (index $parts 1) 2 }}
  {{- if eq (len $credentials) 2 }}
    {{- $hostport := regexSplit "/" (index $credentials 1) 2 }}
    {{- if eq (len $hostport) 2 }}
      {{- $dbname := regexSplit "\\?" (index $hostport 1) 2 }}
      {{- index $dbname 0 }}
    {{- else }}
      {{- "musicevents" }}
    {{- end }}
  {{- else }}
    {{- "musicevents" }}
  {{- end }}
{{- else }}
  {{- "musicevents" }}
{{- end }}
{{- end -}}