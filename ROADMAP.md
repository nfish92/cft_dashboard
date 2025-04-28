## 🛣 Roadmap

Future improvements and feature expansions planned for the CTF Dashboard:

### Short-Term Goals
- [ ] Add flag file encryption to prevent easy flag discovery
- [ ] Implement dynamic folder structure generation with hidden traps and decoys
- [ ] Improve CTF session control (Start, Pause, End features)

### Mid-Term Goals
- [ ] Generate progressively harder folder/file challenges:
  - Password-protected zip files
  - Deeply nested directory puzzles
  - Randomized file permissions requiring escalation
- [ ] Introduce Kali Linux tool usage into challenges:
  - Forced usage of tools like `nmap`, `enum4linux`, `smbclient`, etc.
  - Hidden SMB shares players must discover and access
- [ ] Introduce basic "locking mechanisms" in the folder journey (simulated file locks / dead ends)

### Long-Term Goals
- [ ] Embed mini-games into challenges:
  - Require players to beat Python mini-games (like Pong, Snake, or Space Invaders) to unlock the next file or flag
  - Dynamic challenge popups based on progress
- [ ] Build a lightweight scoreboard and event tracking dashboard
- [ ] Allow multi-player / team sessions (basic matchmaking)
- [ ] Implement randomized daily CTF generator mode for practice
- [ ] Add optional web admin panel for managing game sessions and generating custom CTFs
- [ ] Docker Compose full-stack deployment (web + database + file structure generation)

### Stretch Goals (Wildcard Ideas)
- [ ] Dynamic "CTF Boss Battles" — solve a big complex puzzle at the end (huge file system + multiple tools needed)
- [ ] User profile tracking (stats: number of flags found, average completion time, etc.)
- [ ] API for external integrations (Discord bot notifications when players unlock new flags)

---
